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
ENSEMBLE_RESULTS_PATH = EXPERIMENT_DIR / "ensemble_results.csv"

TRAIN_ENCODING = "cp932"
TEST_ENCODING = "cp932"
SUBMIT_ENCODING = "cp932"
EPS = 1e-8
BAND2_RANGE = (4800.0, 5350.0)
LOCAL_PLS_K = 200
LOCAL_PLS_N_COMP = 3
ENSEMBLE_PAIRS = [
    ("pls_plain", "gbdt_plain"),
    ("pls_log1p", "gbdt_log1p"),
    ("pls_plain", "gbdt_log1p"),
    ("pls_log1p", "gbdt_plain"),
]
ENSEMBLE_WEIGHTS = np.round(np.arange(0.0, 1.01, 0.1), 1)
LGBM_PARAMS = {
    "n_estimators": 500,
    "learning_rate": 0.05,
    "num_leaves": 31,
    "min_child_samples": 20,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "objective": "regression",
    "verbose": -1,
    "random_state": 42,
    "n_jobs": -1,
}


def is_float_column(col_name: str) -> bool:
    try:
        float(col_name)
        return True
    except ValueError:
        return False


def pick_column(columns: list[str], candidates: list[str]) -> str:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    raise KeyError(f"Column not found. candidates={candidates}")


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str], str, str, str]:
    train_df = pd.read_csv(TRAIN_PATH, encoding=TRAIN_ENCODING)
    test_df = pd.read_csv(TEST_PATH, encoding=TEST_ENCODING)
    sample_submit_df = pd.read_csv(
        SAMPLE_SUBMIT_PATH,
        header=None,
        names=["sample_number", "prediction"],
        encoding=SUBMIT_ENCODING,
    )

    train_columns = train_df.columns.tolist()
    test_columns = test_df.columns.tolist()

    sample_col = pick_column(train_columns, ["sample_number", "sample number"])
    if sample_col not in test_columns:
        raise KeyError(f"Sample column {sample_col} not found in test.csv")

    species_col = pick_column(train_columns, ["species", "樹種"])
    target_col = pick_column(train_columns, ["MC", "含水率"])
    wave_cols = [col for col in train_columns if col in test_columns and is_float_column(col)]

    if not wave_cols:
        raise ValueError("No wavelength columns detected.")

    return train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col


def select_band_columns(wave_cols: list[str], wn_range: tuple[float, float]) -> list[str]:
    wn = np.array([float(col) for col in wave_cols], dtype=np.float64)
    mask = (wn >= wn_range[0]) & (wn <= wn_range[1])
    selected = [col for col, keep in zip(wave_cols, mask) if keep]
    if not selected:
        raise ValueError(f"No wavelengths found in range {wn_range}.")
    return selected


def snv(X: np.ndarray) -> np.ndarray:
    row_mean = X.mean(axis=1, keepdims=True)
    row_std = np.clip(X.std(axis=1, keepdims=True), EPS, None)
    return (X - row_mean) / row_std


def sg1(X: np.ndarray) -> np.ndarray:
    return savgol_filter(X, window_length=11, polyorder=2, deriv=1, axis=1)


def snv_sg1(X: np.ndarray) -> np.ndarray:
    return sg1(snv(X))


def normalize_rows(X: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.clip(norms, 1e-12, None)


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def predict_local_pls(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_query: np.ndarray,
    k: int,
    n_comp: int,
) -> np.ndarray:
    if len(X_train) == 0:
        raise ValueError("X_train must not be empty.")

    X_train_norm = normalize_rows(X_train)
    X_query_norm = normalize_rows(X_query)
    similarities = X_query_norm @ X_train_norm.T
    k_eff = min(k, X_train.shape[0])
    topk_idx = np.argpartition(-similarities, kth=k_eff - 1, axis=1)[:, :k_eff]

    preds = np.empty(X_query.shape[0], dtype=np.float64)
    for i, idx in enumerate(topk_idx):
        local_order = np.argsort(-similarities[i, idx])
        idx = idx[local_order]
        X_local = X_train[idx]
        y_local = y_train[idx]
        max_comp = min(n_comp, X_local.shape[0] - 1, X_local.shape[1])

        if max_comp < 1:
            preds[i] = float(np.mean(y_local))
            continue

        model = PLSRegression(n_components=max_comp, max_iter=500)
        model.fit(X_local, y_local)
        preds[i] = float(model.predict(X_query[i : i + 1]).ravel()[0])

    return preds


def predict_gbdt(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_query: np.ndarray,
) -> np.ndarray:
    feature_names = [f"band2_snv_{i:03d}" for i in range(X_train.shape[1])]
    X_train_df = pd.DataFrame(X_train, columns=feature_names)
    X_query_df = pd.DataFrame(X_query, columns=feature_names)
    model = LGBMRegressor(**LGBM_PARAMS)
    model.fit(X_train_df, y_train)
    return model.predict(X_query_df).astype(np.float64)


def evaluate_pls_setting(
    setting_name: str,
    X_proc: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    use_log1p: bool,
) -> np.ndarray:
    logo = LeaveOneGroupOut()
    oof = np.zeros_like(y, dtype=np.float64)

    for fold, (train_idx, valid_idx) in enumerate(logo.split(X_proc, y, groups), start=1):
        y_train_fold = np.log1p(y[train_idx]) if use_log1p else y[train_idx]
        preds = predict_local_pls(
            X_train=X_proc[train_idx],
            y_train=y_train_fold,
            X_query=X_proc[valid_idx],
            k=LOCAL_PLS_K,
            n_comp=LOCAL_PLS_N_COMP,
        )
        if use_log1p:
            preds = np.expm1(preds)
        oof[valid_idx] = preds

        holdout_group = pd.unique(groups[valid_idx]).tolist()
        print(
            f"[{setting_name}] fold={fold} holdout_species={holdout_group} "
            f"train_n={len(train_idx)} valid_n={len(valid_idx)}"
        )

    return oof


def evaluate_gbdt_setting(
    setting_name: str,
    X_proc: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    use_log1p: bool,
) -> np.ndarray:
    logo = LeaveOneGroupOut()
    oof = np.zeros_like(y, dtype=np.float64)

    for fold, (train_idx, valid_idx) in enumerate(logo.split(X_proc, y, groups), start=1):
        y_train_fold = np.log1p(y[train_idx]) if use_log1p else y[train_idx]
        preds = predict_gbdt(
            X_train=X_proc[train_idx],
            y_train=y_train_fold,
            X_query=X_proc[valid_idx],
        )
        if use_log1p:
            preds = np.expm1(preds)
        oof[valid_idx] = preds

        holdout_group = pd.unique(groups[valid_idx]).tolist()
        print(
            f"[{setting_name}] fold={fold} holdout_species={holdout_group} "
            f"train_n={len(train_idx)} valid_n={len(valid_idx)}"
        )

    return oof


def evaluate_all_settings(
    X_band2: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    X_pls = snv_sg1(X_band2)
    X_gbdt = snv(X_band2)

    oof_by_setting = {
        "pls_plain": evaluate_pls_setting("pls_plain", X_pls, y, groups, use_log1p=False),
        "pls_log1p": evaluate_pls_setting("pls_log1p", X_pls, y, groups, use_log1p=True),
        "gbdt_plain": evaluate_gbdt_setting("gbdt_plain", X_gbdt, y, groups, use_log1p=False),
        "gbdt_log1p": evaluate_gbdt_setting("gbdt_log1p", X_gbdt, y, groups, use_log1p=True),
    }

    results = [
        {"setting": setting_name, "loso_rmse": rmse(y, preds)}
        for setting_name, preds in oof_by_setting.items()
    ]
    results_df = pd.DataFrame(results).sort_values("loso_rmse", kind="stable").reset_index(drop=True)
    return results_df, oof_by_setting


def search_ensemble(
    y: np.ndarray,
    oof_by_setting: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, pd.Series]:
    rows: list[dict[str, float | str]] = []
    for pls_setting, gbdt_setting in ENSEMBLE_PAIRS:
        oof_pls = oof_by_setting[pls_setting]
        oof_gbdt = oof_by_setting[gbdt_setting]
        for w_pls in ENSEMBLE_WEIGHTS:
            ensemble_oof = w_pls * oof_pls + (1.0 - w_pls) * oof_gbdt
            rows.append(
                {
                    "pls_setting": pls_setting,
                    "gbdt_setting": gbdt_setting,
                    "w_pls": float(w_pls),
                    "ensemble_rmse": rmse(y, ensemble_oof),
                }
            )

    ensemble_df = pd.DataFrame(rows).sort_values("ensemble_rmse", kind="stable").reset_index(drop=True)
    return ensemble_df, ensemble_df.iloc[0]


def fit_predict_full(
    setting_name: str,
    X_train_band2: np.ndarray,
    y_train: np.ndarray,
    X_test_band2: np.ndarray,
) -> np.ndarray:
    if setting_name == "pls_plain":
        return predict_local_pls(
            X_train=snv_sg1(X_train_band2),
            y_train=y_train,
            X_query=snv_sg1(X_test_band2),
            k=LOCAL_PLS_K,
            n_comp=LOCAL_PLS_N_COMP,
        )

    if setting_name == "pls_log1p":
        preds = predict_local_pls(
            X_train=snv_sg1(X_train_band2),
            y_train=np.log1p(y_train),
            X_query=snv_sg1(X_test_band2),
            k=LOCAL_PLS_K,
            n_comp=LOCAL_PLS_N_COMP,
        )
        return np.expm1(preds)

    if setting_name == "gbdt_plain":
        return predict_gbdt(
            X_train=snv(X_train_band2),
            y_train=y_train,
            X_query=snv(X_test_band2),
        )

    if setting_name == "gbdt_log1p":
        preds = predict_gbdt(
            X_train=snv(X_train_band2),
            y_train=np.log1p(y_train),
            X_query=snv(X_test_band2),
        )
        return np.expm1(preds)

    raise ValueError(f"Unknown setting: {setting_name}")


def save_submission(
    sample_submit_df: pd.DataFrame,
    test_df: pd.DataFrame,
    sample_col: str,
    preds: np.ndarray,
    out_path: Path,
) -> None:
    pred_df = pd.DataFrame(
        {
            "sample_number": test_df[sample_col].to_numpy(),
            "prediction": preds,
        }
    )
    submission_df = sample_submit_df[["sample_number"]].merge(
        pred_df,
        on="sample_number",
        how="left",
        validate="one_to_one",
    )
    if submission_df["prediction"].isna().any():
        missing = submission_df.loc[submission_df["prediction"].isna(), "sample_number"].tolist()
        raise ValueError(f"Missing predictions for sample_number values: {missing}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    submission_df.to_csv(out_path, index=False, header=False, encoding=SUBMIT_ENCODING)


def main() -> None:
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)

    train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col = load_data()
    band2_cols = select_band_columns(wave_cols, BAND2_RANGE)

    X_train_band2 = train_df[band2_cols].to_numpy(dtype=np.float64)
    X_test_band2 = test_df[band2_cols].to_numpy(dtype=np.float64)
    y_train = train_df[target_col].to_numpy(dtype=np.float64)
    groups = train_df[species_col].to_numpy()

    if np.any(y_train < 0):
        raise ValueError("Target contains negative values, cannot apply log1p safely.")

    print(f"train_shape={train_df.shape}")
    print(f"test_shape={test_df.shape}")
    print(f"sample_col={sample_col}")
    print(f"species_col={species_col}")
    print(f"target_col={target_col}")
    print(f"band2_range_cm-1={BAND2_RANGE}")
    print(f"band2_feature_count={len(band2_cols)}")
    print(f"local_pls_k={LOCAL_PLS_K}")
    print(f"local_pls_n_comp={LOCAL_PLS_N_COMP}")
    print("")

    results_df, oof_by_setting = evaluate_all_settings(X_train_band2, y_train, groups)
    results_df.to_csv(RESULTS_PATH, index=False, encoding="utf-8")

    print("=== Setting RMSE ===")
    print(results_df.to_string(index=False))
    print(f"saved_results={RESULTS_PATH}")
    print("")

    ensemble_df, best_ensemble = search_ensemble(y_train, oof_by_setting)
    ensemble_df.to_csv(ENSEMBLE_RESULTS_PATH, index=False, encoding="utf-8")

    print("=== Ensemble RMSE Top 10 ===")
    print(ensemble_df.head(10).to_string(index=False))
    print(f"saved_ensemble_results={ENSEMBLE_RESULTS_PATH}")
    print("")

    best_pls_setting = str(best_ensemble["pls_setting"])
    best_gbdt_setting = str(best_ensemble["gbdt_setting"])
    best_w_pls = float(best_ensemble["w_pls"])
    best_rmse_value = float(best_ensemble["ensemble_rmse"])
    ensemble_name = f"{best_pls_setting}_{best_gbdt_setting}_w{best_w_pls:.1f}"

    print(
        f"best_ensemble pls_setting={best_pls_setting} "
        f"gbdt_setting={best_gbdt_setting} w_pls={best_w_pls:.1f} "
        f"ensemble_rmse={best_rmse_value:.6f}"
    )

    pls_test_preds = fit_predict_full(best_pls_setting, X_train_band2, y_train, X_test_band2)
    gbdt_test_preds = fit_predict_full(best_gbdt_setting, X_train_band2, y_train, X_test_band2)
    ensemble_test_preds = best_w_pls * pls_test_preds + (1.0 - best_w_pls) * gbdt_test_preds

    print(f"test_pred_min={ensemble_test_preds.min():.6f}")
    print(f"test_pred_max={ensemble_test_preds.max():.6f}")

    negative_mask = ensemble_test_preds < 0
    if np.any(negative_mask):
        negative_values = ensemble_test_preds[negative_mask]
        print(
            f"negative_predictions_detected count={int(negative_mask.sum())} "
            f"values={negative_values.tolist()}"
        )
        print("submission_skipped=True")
        return

    submission_path = SUBMISSIONS_DIR / f"expEnsemble_log1p_{ensemble_name}_submission.csv"
    save_submission(sample_submit_df, test_df, sample_col, ensemble_test_preds, submission_path)
    print(f"saved_submission={submission_path}")


if __name__ == "__main__":
    main()
