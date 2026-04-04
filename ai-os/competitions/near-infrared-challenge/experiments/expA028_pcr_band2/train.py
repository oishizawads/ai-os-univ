from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
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
EPS = 1e-8

PREPROCESSINGS = ["snv", "snv_sg1"]
N_COMPONENTS_LIST = [3, 5, 8, 10, 15, 20, 30]
ALPHAS = [0.01, 0.1, 1.0, 10.0, 100.0]


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


def apply_preprocessing(X: np.ndarray, method: str) -> np.ndarray:
    X = X.astype(np.float64, copy=True)
    row_mean = X.mean(axis=1, keepdims=True)
    row_std = np.clip(X.std(axis=1, keepdims=True), EPS, None)
    X = (X - row_mean) / row_std
    if method == "snv":
        return X
    if method == "snv_sg1":
        return savgol_filter(X, window_length=11, polyorder=2, deriv=1, axis=1)
    raise ValueError(f"Unknown preprocessing: {method}")


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

    print(f"train_shape={train_df.shape}, test_shape={test_df.shape}")
    print(f"band2_feature_count={len(band2_cols)}")

    logo = LeaveOneGroupOut()
    total = len(PREPROCESSINGS) * len(N_COMPONENTS_LIST) * len(ALPHAS)
    done = 0
    results = []

    for preproc in PREPROCESSINGS:
        X_proc = apply_preprocessing(X_train_raw, preproc)
        for n_comp in N_COMPONENTS_LIST:
            for alpha in ALPHAS:
                oof = np.zeros_like(y_train, dtype=np.float64)
                for train_idx, valid_idx in logo.split(X_proc, y_train, groups):
                    pca = PCA(n_components=n_comp, random_state=42)
                    X_tr_pca = pca.fit_transform(X_proc[train_idx])
                    X_val_pca = pca.transform(X_proc[valid_idx])
                    ridge = Ridge(alpha=alpha)
                    ridge.fit(X_tr_pca, y_train[train_idx])
                    oof[valid_idx] = ridge.predict(X_val_pca)

                rmse = float(np.sqrt(mean_squared_error(y_train, oof)))
                results.append({"preproc": preproc, "n_components": n_comp, "alpha": alpha, "loso_rmse": rmse})
                done += 1
                print(f"[{done}/{total}] preproc={preproc} n_comp={n_comp} alpha={alpha} loso_rmse={rmse:.6f}")

    results_df = pd.DataFrame(results).sort_values("loso_rmse", kind="stable").reset_index(drop=True)
    results_df.to_csv(RESULTS_PATH, index=False, encoding="utf-8")
    print(f"\nsaved_results={RESULTS_PATH}")
    print("Top 10:")
    print(results_df.head(10).to_string(index=False))

    best = results_df.iloc[0]
    best_preproc = str(best["preproc"])
    best_n_comp = int(best["n_components"])
    best_alpha = float(best["alpha"])
    best_rmse = float(best["loso_rmse"])
    print(f"\nbest: preproc={best_preproc} n_comp={best_n_comp} alpha={best_alpha} loso_rmse={best_rmse:.6f}")

    # Test predictions
    X_train_proc = apply_preprocessing(X_train_raw, best_preproc)
    X_test_proc = apply_preprocessing(X_test_raw, best_preproc)
    pca_final = PCA(n_components=best_n_comp, random_state=42)
    X_train_pca = pca_final.fit_transform(X_train_proc)
    X_test_pca = pca_final.transform(X_test_proc)
    ridge_final = Ridge(alpha=best_alpha)
    ridge_final.fit(X_train_pca, y_train)
    test_preds = ridge_final.predict(X_test_pca)

    print(f"test_pred_min={test_preds.min():.4f}, max={test_preds.max():.4f}")

    if np.any(test_preds < 0):
        print(f"negative_predictions_detected count={np.sum(test_preds < 0)}")
        print("submission_skipped=True")
        return

    submission_path = SUBMISSIONS_DIR / f"expA028_pcr_band2_{best_preproc}_n{best_n_comp}_a{best_alpha}_submission.csv"
    save_submission(sample_submit_df, test_df, sample_col, test_preds, submission_path)
    print(f"saved_submission={submission_path}")


if __name__ == "__main__":
    main()
