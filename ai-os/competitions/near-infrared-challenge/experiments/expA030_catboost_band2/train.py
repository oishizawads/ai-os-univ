from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
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

SETTINGS = [
    ("band2_snv_catboost", None),
    ("band2_snv_pca10_catboost", 10),
    ("band2_snv_pca20_catboost", 20),
]

CATBOOST_PARAMS = {
    "iterations": 500,
    "learning_rate": 0.05,
    "depth": 6,
    "loss_function": "RMSE",
    "random_seed": 42,
    "verbose": 0,
    "thread_count": -1,
}


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
        SAMPLE_SUBMIT_PATH, header=None, names=["sample_number", "prediction"], encoding=SUBMIT_ENCODING
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


def build_features(X_train, X_valid, pca_components):
    from sklearn.decomposition import PCA
    X_train_snv = apply_snv(X_train)
    X_valid_snv = apply_snv(X_valid)
    if pca_components is None:
        return X_train_snv, X_valid_snv
    pca = PCA(n_components=pca_components, random_state=42)
    return pca.fit_transform(X_train_snv), pca.transform(X_valid_snv)


def save_submission(sample_submit_df, test_df, sample_col, preds, out_path):
    pred_df = pd.DataFrame({"sample_number": test_df[sample_col].to_numpy(), "prediction": preds})
    submission_df = sample_submit_df[["sample_number"]].merge(pred_df, on="sample_number", how="left", validate="one_to_one")
    if submission_df["prediction"].isna().any():
        raise ValueError("Missing predictions")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    submission_df.to_csv(out_path, index=False, header=False, encoding=SUBMIT_ENCODING)


def main():
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
    train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col = load_data()
    band2_cols = select_band_columns(wave_cols, BAND2_RANGE)

    X_train = train_df[band2_cols].to_numpy(dtype=np.float64)
    y_train = train_df[target_col].to_numpy(dtype=np.float64)
    groups = train_df[species_col].to_numpy()
    X_test = test_df[band2_cols].to_numpy(dtype=np.float64)

    print(f"train_shape={train_df.shape}, band2_feature_count={len(band2_cols)}")

    logo = LeaveOneGroupOut()
    results = []
    best_rmse = float("inf")
    best_setting = None

    for setting_name, pca_components in SETTINGS:
        oof = np.zeros_like(y_train, dtype=np.float64)
        for fold, (train_idx, valid_idx) in enumerate(logo.split(X_train, y_train, groups), 1):
            X_tr, X_val = build_features(X_train[train_idx], X_train[valid_idx], pca_components)
            model = CatBoostRegressor(**CATBOOST_PARAMS)
            model.fit(X_tr, y_train[train_idx])
            oof[valid_idx] = model.predict(X_val)
            holdout = np.unique(groups[valid_idx]).tolist()
            fold_rmse = float(np.sqrt(mean_squared_error(y_train[valid_idx], oof[valid_idx])))
            print(f"  [{setting_name}] fold={fold} holdout={holdout} rmse={fold_rmse:.4f}")

        rmse = float(np.sqrt(mean_squared_error(y_train, oof)))
        results.append({"setting": setting_name, "loso_rmse": rmse})
        print(f"[{setting_name}] LOSO RMSE = {rmse:.6f}\n")
        if rmse < best_rmse:
            best_rmse = rmse
            best_setting = (setting_name, pca_components)

    results_df = pd.DataFrame(results).sort_values("loso_rmse", kind="stable").reset_index(drop=True)
    results_df.to_csv(RESULTS_PATH, index=False, encoding="utf-8")
    print(results_df.to_string(index=False))
    print(f"\nsaved_results={RESULTS_PATH}")

    best_name, best_pca = best_setting
    X_tr_best, X_test_best = build_features(X_train, X_test, best_pca)
    final_model = CatBoostRegressor(**CATBOOST_PARAMS)
    final_model.fit(X_tr_best, y_train)
    test_preds = final_model.predict(X_test_best)

    print(f"\nbest_setting={best_name}, loso_rmse={best_rmse:.6f}")
    print(f"test_pred_min={test_preds.min():.4f}, max={test_preds.max():.4f}")

    if np.any(test_preds < 0):
        print(f"negative_predictions_detected count={np.sum(test_preds < 0)}, submission_skipped=True")
        return

    submission_path = SUBMISSIONS_DIR / f"expA030_catboost_band2_{best_name}_submission.csv"
    save_submission(sample_submit_df, test_df, sample_col, test_preds, submission_path)
    print(f"saved_submission={submission_path}")


if __name__ == "__main__":
    main()
