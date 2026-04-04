from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.decomposition import PCA
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
    ("band2_snv_lgbm", None),
    ("band2_snv_pca20_lgbm", 20),
    ("band2_snv_pca10_lgbm", 10),
]

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
    sample_col = pick_column(train_columns, ["sample_number", "sample number"], fallback_index=0)
    species_col = pick_column(train_columns, ["species", "樹種"], fallback_index=2)
    target_col = pick_column(train_columns, ["MC", "含水率"], fallback_index=3)
    wave_cols = [col for col in train_columns if is_float_column(col)]

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


def apply_snv(X: np.ndarray) -> np.ndarray:
    row_mean = X.mean(axis=1, keepdims=True)
    row_std = np.clip(X.std(axis=1, keepdims=True), EPS, None)
    return (X - row_mean) / row_std


def build_features(
    X_train: np.ndarray,
    X_valid: np.ndarray,
    pca_components: int | None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    X_train_snv = apply_snv(X_train)
    X_valid_snv = apply_snv(X_valid)

    if pca_components is None:
        columns = [f"band2_{i:03d}" for i in range(X_train_snv.shape[1])]
        return pd.DataFrame(X_train_snv, columns=columns), pd.DataFrame(X_valid_snv, columns=columns)

    pca = PCA(n_components=pca_components, random_state=42)
    X_train_pca = pca.fit_transform(X_train_snv)
    X_valid_pca = pca.transform(X_valid_snv)
    columns = [f"pca_{i:02d}" for i in range(pca_components)]
    return pd.DataFrame(X_train_pca, columns=columns), pd.DataFrame(X_valid_pca, columns=columns)


def run_loso(
    X: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    setting_name: str,
    pca_components: int | None,
) -> tuple[float, np.ndarray]:
    logo = LeaveOneGroupOut()
    oof = np.zeros_like(y, dtype=np.float64)

    for fold, (train_idx, valid_idx) in enumerate(logo.split(X, y, groups), start=1):
        X_train_fold, X_valid_fold = build_features(X[train_idx], X[valid_idx], pca_components)
        y_train_fold = y[train_idx]

        model = LGBMRegressor(**LGBM_PARAMS)
        model.fit(X_train_fold, y_train_fold)
        oof[valid_idx] = model.predict(X_valid_fold)

        holdout_group = pd.unique(groups[valid_idx]).tolist()
        print(
            f"[{setting_name}] fold={fold} holdout_species={holdout_group} "
            f"train_n={len(train_idx)} valid_n={len(valid_idx)}"
        )

    rmse = float(np.sqrt(mean_squared_error(y, oof)))
    return rmse, oof


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

    X_train = train_df[band2_cols].to_numpy(dtype=np.float64)
    y_train = train_df[target_col].to_numpy(dtype=np.float64)
    groups = train_df[species_col].to_numpy()
    X_test = test_df[band2_cols].to_numpy(dtype=np.float64)

    print(f"train_shape={train_df.shape}")
    print(f"test_shape={test_df.shape}")
    print(f"sample_col={sample_col}")
    print(f"species_col={species_col}")
    print(f"target_col={target_col}")
    print(f"band2_range_cm-1={BAND2_RANGE}")
    print(f"band2_feature_count={len(band2_cols)}")
    print("")

    results: list[dict[str, float | str]] = []
    best_setting = None
    best_rmse = float("inf")

    for setting_name, pca_components in SETTINGS:
        rmse, _ = run_loso(X_train, y_train, groups, setting_name, pca_components)
        results.append({"setting": setting_name, "loso_rmse": rmse})
        print(f"{setting_name}: loso_rmse={rmse:.6f}")

        if rmse < best_rmse:
            best_rmse = rmse
            best_setting = (setting_name, pca_components)

    results_df = pd.DataFrame(results).sort_values("loso_rmse", kind="stable").reset_index(drop=True)
    results_df.to_csv(RESULTS_PATH, index=False, encoding="utf-8")

    print("")
    print(results_df.to_string(index=False))
    print(f"saved_results={RESULTS_PATH}")

    if best_setting is None:
        raise RuntimeError("No setting was evaluated.")

    best_name, best_pca_components = best_setting
    X_train_best, X_test_best = build_features(X_train, X_test, best_pca_components)
    best_model = LGBMRegressor(**LGBM_PARAMS)
    best_model.fit(X_train_best, y_train)
    test_preds = best_model.predict(X_test_best)

    print("")
    print(f"best_setting={best_name}")
    print(f"best_loso_rmse={best_rmse:.6f}")
    print(f"test_pred_min={test_preds.min():.6f}")
    print(f"test_pred_max={test_preds.max():.6f}")

    negative_mask = test_preds < 0
    if np.any(negative_mask):
        negative_values = test_preds[negative_mask]
        print(f"negative_predictions_detected count={negative_mask.sum()} values={negative_values.tolist()}")
        print("submission_skipped=True")
        return

    submission_path = SUBMISSIONS_DIR / f"expGBDT_band2_{best_name}_submission.csv"
    save_submission(sample_submit_df, test_df, sample_col, test_preds, submission_path)
    print(f"saved_submission={submission_path}")


if __name__ == "__main__":
    main()
