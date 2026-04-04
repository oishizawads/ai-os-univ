from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from scipy.signal import savgol_filter
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"
EXPERIMENT_DIR = Path(__file__).resolve().parent
SUBMISSIONS_DIR = PROJECT_ROOT / "submissions"

TRAIN_PATH = DATA_DIR / "train.csv"
TEST_PATH = DATA_DIR / "test.csv"
SAMPLE_SUBMIT_PATH = DATA_DIR / "sample_submit.csv"
RESULTS_PATH = EXPERIMENT_DIR / "results.csv"

TRAIN_ENCODING = "cp932"
TEST_ENCODING = "cp932"
SUBMIT_ENCODING = "cp932"

BAND2_RANGE = (4800.0, 5350.0)

# LocalPLS best config (from expLocalPLS_band2 results, first non-negative)
LOCALPLS_PREPROC = "snv_sg1"
LOCALPLS_K = 200
LOCALPLS_N_COMP = 3

# GBDT best config (from expGBDT_band2 results)
GBDT_PCA_COMPONENTS = None  # raw SNV, no PCA

LGBM_PARAMS = {
    "n_estimators": 500,
    "learning_rate": 0.05,
    "num_leaves": 31,
    "min_child_samples": 20,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "objective": "regression",
    "metric": "rmse",
    "verbose": -1,
    "random_state": 42,
    "n_jobs": -1,
}

EPS = 1e-8


def is_float_column(col_name: str) -> bool:
    try:
        float(col_name)
        return True
    except ValueError:
        return False


def pick_column(columns: list[str], candidates: list[str], fallback_index: int | None = None) -> str:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    if fallback_index is not None:
        return columns[fallback_index]
    raise KeyError(f"Column not found. candidates={candidates}")


def load_data():
    train_df = pd.read_csv(TRAIN_PATH, encoding=TRAIN_ENCODING)
    test_df = pd.read_csv(TEST_PATH, encoding=TEST_ENCODING)
    sample_submit_df = pd.read_csv(
        SAMPLE_SUBMIT_PATH,
        header=None,
        names=["sample_number", "prediction"],
        encoding=SUBMIT_ENCODING,
    )
    train_columns = train_df.columns.tolist()
    sample_col = pick_column(train_columns, ["sample_number", "sample number"], fallback_index=0)
    species_col = pick_column(train_columns, ["species", "樹種"], fallback_index=2)
    target_col = pick_column(train_columns, ["MC", "含水率"], fallback_index=3)
    wave_cols = [col for col in train_columns if is_float_column(col)]
    return train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col


def select_band_columns(wave_cols: list[str], wn_range: tuple[float, float]) -> list[str]:
    wn = np.array([float(col) for col in wave_cols], dtype=np.float64)
    mask = (wn >= wn_range[0]) & (wn <= wn_range[1])
    return [col for col, keep in zip(wave_cols, mask) if keep]


def apply_snv(X: np.ndarray) -> np.ndarray:
    row_mean = X.mean(axis=1, keepdims=True)
    row_std = np.clip(X.std(axis=1, keepdims=True), EPS, None)
    return (X - row_mean) / row_std


def apply_preprocessing_localpls(X: np.ndarray, method: str) -> np.ndarray:
    X = X.astype(np.float64, copy=True)
    if method == "raw":
        return X
    row_mean = X.mean(axis=1, keepdims=True)
    row_std = np.clip(X.std(axis=1, keepdims=True), EPS, None)
    X = (X - row_mean) / row_std
    if method == "snv":
        return X
    if method == "snv_sg1":
        return savgol_filter(X, window_length=11, polyorder=2, deriv=1, axis=1)
    raise ValueError(f"Unknown preprocessing: {method}")


def normalize_rows(X: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.clip(norms, 1e-12, None)


def predict_local_pls(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_query: np.ndarray,
    k: int,
    n_comp: int,
) -> np.ndarray:
    k_eff = min(k, len(X_train))
    X_train_norm = normalize_rows(X_train)
    X_query_norm = normalize_rows(X_query)
    similarities = X_query_norm @ X_train_norm.T
    topk_idx = np.argpartition(-similarities, kth=k_eff - 1, axis=1)[:, :k_eff]

    preds: list[float] = []
    for i, idx in enumerate(topk_idx):
        local_order = np.argsort(-similarities[i, idx])
        idx = idx[local_order]
        X_local = X_train[idx]
        y_local = y_train[idx]
        max_comp = min(n_comp, X_local.shape[0] - 1, X_local.shape[1])
        if max_comp < 1:
            preds.append(float(np.mean(y_local)))
            continue
        model = PLSRegression(n_components=max_comp, max_iter=500)
        model.fit(X_local, y_local)
        pred = model.predict(X_query[i : i + 1]).ravel()[0]
        preds.append(float(pred))
    return np.array(preds, dtype=np.float64)


def save_submission(
    sample_submit_df: pd.DataFrame,
    test_df: pd.DataFrame,
    sample_col: str,
    preds: np.ndarray,
    out_path: Path,
) -> None:
    pred_df = pd.DataFrame({"sample_number": test_df[sample_col].to_numpy(), "prediction": preds})
    submission_df = sample_submit_df[["sample_number"]].merge(
        pred_df, on="sample_number", how="left", validate="one_to_one"
    )
    if submission_df["prediction"].isna().any():
        missing = submission_df.loc[submission_df["prediction"].isna(), "sample_number"].tolist()
        raise ValueError(f"Missing predictions: {missing}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    submission_df.to_csv(out_path, index=False, header=False, encoding=SUBMIT_ENCODING)


def main() -> None:
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)

    train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col = load_data()
    band2_cols = select_band_columns(wave_cols, BAND2_RANGE)

    X_train_raw = train_df[band2_cols].to_numpy(dtype=np.float64)
    y_train = train_df[target_col].to_numpy(dtype=np.float64)
    groups = train_df[species_col].to_numpy()
    X_test_raw = test_df[band2_cols].to_numpy(dtype=np.float64)
    sample_numbers_train = train_df[sample_col].to_numpy()

    print(f"train_shape={train_df.shape}, test_shape={test_df.shape}")
    print(f"band2_feature_count={len(band2_cols)}")

    logo = LeaveOneGroupOut()

    # --- LocalPLS OOF ---
    print("\n[LocalPLS] Generating OOF ...")
    localpls_oof = np.zeros_like(y_train, dtype=np.float64)
    X_train_proc = apply_preprocessing_localpls(X_train_raw, LOCALPLS_PREPROC)
    for fold, (train_idx, valid_idx) in enumerate(logo.split(X_train_proc, y_train, groups), 1):
        preds = predict_local_pls(
            X_train=X_train_proc[train_idx],
            y_train=y_train[train_idx],
            X_query=X_train_proc[valid_idx],
            k=LOCALPLS_K,
            n_comp=LOCALPLS_N_COMP,
        )
        localpls_oof[valid_idx] = preds
        holdout = np.unique(groups[valid_idx]).tolist()
        fold_rmse = float(np.sqrt(mean_squared_error(y_train[valid_idx], preds)))
        print(f"  fold={fold} holdout={holdout} rmse={fold_rmse:.4f}")

    localpls_loso_rmse = float(np.sqrt(mean_squared_error(y_train, localpls_oof)))
    print(f"LocalPLS LOSO RMSE = {localpls_loso_rmse:.6f}")

    # Save LocalPLS OOF
    localpls_oof_path = PROJECT_ROOT / "experiments" / "expLocalPLS_band2" / "oof_predictions.csv"
    pd.DataFrame({
        "sample_number": sample_numbers_train,
        "oof_pred": localpls_oof,
        "true_mc": y_train,
    }).to_csv(localpls_oof_path, index=False, encoding="utf-8")
    print(f"saved localpls_oof={localpls_oof_path}")

    # --- GBDT OOF ---
    print("\n[GBDT] Generating OOF ...")
    gbdt_oof = np.zeros_like(y_train, dtype=np.float64)
    X_train_snv = apply_snv(X_train_raw)
    for fold, (train_idx, valid_idx) in enumerate(logo.split(X_train_snv, y_train, groups), 1):
        model = LGBMRegressor(**LGBM_PARAMS)
        model.fit(X_train_snv[train_idx], y_train[train_idx])
        gbdt_oof[valid_idx] = model.predict(X_train_snv[valid_idx])
        holdout = np.unique(groups[valid_idx]).tolist()
        fold_rmse = float(np.sqrt(mean_squared_error(y_train[valid_idx], gbdt_oof[valid_idx])))
        print(f"  fold={fold} holdout={holdout} rmse={fold_rmse:.4f}")

    gbdt_loso_rmse = float(np.sqrt(mean_squared_error(y_train, gbdt_oof)))
    print(f"GBDT LOSO RMSE = {gbdt_loso_rmse:.6f}")

    # Save GBDT OOF
    gbdt_oof_path = PROJECT_ROOT / "experiments" / "expGBDT_band2" / "oof_predictions.csv"
    pd.DataFrame({
        "sample_number": sample_numbers_train,
        "oof_pred": gbdt_oof,
        "true_mc": y_train,
    }).to_csv(gbdt_oof_path, index=False, encoding="utf-8")
    print(f"saved gbdt_oof={gbdt_oof_path}")

    # --- Optimal weight search ---
    print("\n[Ensemble] Searching optimal weight ...")
    weights = np.arange(0.0, 1.01, 0.1)
    weight_results = []
    for w in weights:
        ens_oof = w * localpls_oof + (1.0 - w) * gbdt_oof
        rmse = float(np.sqrt(mean_squared_error(y_train, ens_oof)))
        weight_results.append({"w": round(float(w), 1), "ensemble_loso_rmse": rmse})
        print(f"  w={w:.1f} ensemble_rmse={rmse:.6f}")

    results_df = pd.DataFrame(weight_results)
    results_df["localpls_loso_rmse"] = localpls_loso_rmse
    results_df["gbdt_loso_rmse"] = gbdt_loso_rmse
    results_df = results_df[["w", "localpls_loso_rmse", "gbdt_loso_rmse", "ensemble_loso_rmse"]]
    results_df = results_df.sort_values("ensemble_loso_rmse", kind="stable").reset_index(drop=True)
    results_df.to_csv(RESULTS_PATH, index=False, encoding="utf-8")
    print(f"\nsaved_results={RESULTS_PATH}")
    print(results_df.head(5).to_string(index=False))

    best_w = float(results_df.iloc[0]["w"])
    best_ensemble_rmse = float(results_df.iloc[0]["ensemble_loso_rmse"])
    print(f"\nbest_w={best_w}, best_ensemble_loso_rmse={best_ensemble_rmse:.6f}")

    # --- Test predictions ---
    print("\n[Test] Generating test predictions ...")
    X_test_localpls = apply_preprocessing_localpls(X_test_raw, LOCALPLS_PREPROC)
    X_train_localpls = apply_preprocessing_localpls(X_train_raw, LOCALPLS_PREPROC)
    localpls_test_preds = predict_local_pls(
        X_train=X_train_localpls,
        y_train=y_train,
        X_query=X_test_localpls,
        k=LOCALPLS_K,
        n_comp=LOCALPLS_N_COMP,
    )

    X_test_snv = apply_snv(X_test_raw)
    gbdt_model = LGBMRegressor(**LGBM_PARAMS)
    gbdt_model.fit(X_train_snv, y_train)
    gbdt_test_preds = gbdt_model.predict(X_test_snv)

    ensemble_test_preds = best_w * localpls_test_preds + (1.0 - best_w) * gbdt_test_preds

    print(f"localpls_test_min={localpls_test_preds.min():.4f}, max={localpls_test_preds.max():.4f}")
    print(f"gbdt_test_min={gbdt_test_preds.min():.4f}, max={gbdt_test_preds.max():.4f}")
    print(f"ensemble_test_min={ensemble_test_preds.min():.4f}, max={ensemble_test_preds.max():.4f}")

    if np.any(ensemble_test_preds < 0):
        print(f"negative_predictions_detected count={np.sum(ensemble_test_preds < 0)}")
        print("submission_skipped=True")
        return

    submission_path = SUBMISSIONS_DIR / f"expA027_ensemble_localpls_gbdt_w{best_w:.1f}_submission.csv"
    save_submission(sample_submit_df, test_df, sample_col, ensemble_test_preds, submission_path)
    print(f"saved_submission={submission_path}")


if __name__ == "__main__":
    main()
