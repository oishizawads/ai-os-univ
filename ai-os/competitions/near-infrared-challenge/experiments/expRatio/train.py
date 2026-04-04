from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from sklearn.cross_decomposition import PLSRegression
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut

DATA_ENCODING = "cp932"
EXPERIMENT_ID = "expRatio"
PROJECT_ROOT = Path("C:/workspace/ai-os/competitions/near-infrared-challenge")
EXPERIMENT_DIR = PROJECT_ROOT / "experiments" / EXPERIMENT_ID
SUBMISSIONS_DIR = PROJECT_ROOT / "submissions"

TRAIN_CANDIDATES = [
    PROJECT_ROOT / "data" / "train.csv",
    PROJECT_ROOT / "data" / "raw" / "train.csv",
]
TEST_CANDIDATES = [
    PROJECT_ROOT / "data" / "test.csv",
    PROJECT_ROOT / "data" / "raw" / "test.csv",
]
SAMPLE_SUBMIT_CANDIDATES = [
    PROJECT_ROOT / "data" / "sample_submit.csv",
    PROJECT_ROOT / "data" / "raw" / "sample_submit.csv",
]

BAND2_RANGE = (4800.0, 5350.0)
REF_BANDS = {
    "refA": (4050.0, 4100.0),
    "refB": (7000.0, 7200.0),
}
FEATURES = ["ratio_refA", "ratio_refB", "band2_raw", "band2_snv", "band2_snv_sg2"]
N_COMPONENTS_GRID = [1, 2, 3, 5, 8, 10]


def resolve_existing_path(candidates: list[Path]) -> Path:
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(f"None of the candidate paths exist: {candidates}")


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_path = resolve_existing_path(TRAIN_CANDIDATES)
    test_path = resolve_existing_path(TEST_CANDIDATES)
    sample_submit_path = resolve_existing_path(SAMPLE_SUBMIT_CANDIDATES)

    train_df = pd.read_csv(train_path, encoding=DATA_ENCODING)
    test_df = pd.read_csv(test_path, encoding=DATA_ENCODING)
    sample_submit_df = pd.read_csv(
        sample_submit_path,
        header=None,
        names=["sample_number", "MC"],
        encoding=DATA_ENCODING,
    )
    return train_df, test_df, sample_submit_df


def standardize_columns(df: pd.DataFrame, is_train: bool) -> pd.DataFrame:
    rename_map = {
        "sample number": "sample_number",
        "species number": "species_number",
        "樹種": "species",
    }
    if is_train:
        rename_map["含水率"] = "MC"
    return df.rename(columns=rename_map)


def wave_columns(df: pd.DataFrame) -> list[str]:
    cols: list[str] = []
    for col in df.columns:
        try:
            float(col)
            cols.append(col)
        except (TypeError, ValueError):
            continue
    return cols


def snv(x: np.ndarray) -> np.ndarray:
    row_mean = x.mean(axis=1, keepdims=True)
    row_std = x.std(axis=1, keepdims=True)
    return (x - row_mean) / np.clip(row_std, 1e-8, None)


def sg2(x: np.ndarray) -> np.ndarray:
    return savgol_filter(x, window_length=11, polyorder=2, deriv=2, axis=1)


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def make_masks(wavenumbers: np.ndarray) -> dict[str, np.ndarray]:
    masks = {"band2": (wavenumbers >= BAND2_RANGE[0]) & (wavenumbers <= BAND2_RANGE[1])}
    for key, (low, high) in REF_BANDS.items():
        masks[key] = (wavenumbers >= low) & (wavenumbers <= high)
    return masks


def build_feature_matrices(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    wave_cols: list[str],
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    wavenumbers = np.array([float(col) for col in wave_cols], dtype=float)
    masks = make_masks(wavenumbers)

    x_train_full = train_df[wave_cols].to_numpy(dtype=float)
    x_test_full = test_df[wave_cols].to_numpy(dtype=float)

    band2_train = x_train_full[:, masks["band2"]]
    band2_test = x_test_full[:, masks["band2"]]

    ref_a_train = x_train_full[:, masks["refA"]].mean(axis=1, keepdims=True)
    ref_a_test = x_test_full[:, masks["refA"]].mean(axis=1, keepdims=True)
    ref_b_train = x_train_full[:, masks["refB"]].mean(axis=1, keepdims=True)
    ref_b_test = x_test_full[:, masks["refB"]].mean(axis=1, keepdims=True)

    band2_mean_train = band2_train.mean(axis=1, keepdims=True)
    band2_mean_test = band2_test.mean(axis=1, keepdims=True)

    band2_snv_train = snv(band2_train)
    band2_snv_test = snv(band2_test)

    feature_map = {
        "ratio_refA": (
            band2_mean_train / np.clip(ref_a_train, 1e-8, None),
            band2_mean_test / np.clip(ref_a_test, 1e-8, None),
        ),
        "ratio_refB": (
            band2_mean_train / np.clip(ref_b_train, 1e-8, None),
            band2_mean_test / np.clip(ref_b_test, 1e-8, None),
        ),
        "band2_raw": (band2_train, band2_test),
        "band2_snv": (band2_snv_train, band2_snv_test),
        "band2_snv_sg2": (sg2(band2_snv_train), sg2(band2_snv_test)),
    }
    return feature_map


def fit_predict(
    feature_name: str,
    n_comp: int,
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_valid: np.ndarray,
) -> np.ndarray:
    if feature_name.startswith("ratio_"):
        model = LinearRegression()
        model.fit(x_train, y_train)
        return model.predict(x_valid)

    max_components = min(n_comp, x_train.shape[1], x_train.shape[0] - 1)
    if max_components < 1:
        raise ValueError(f"Invalid number of PLS components for {feature_name}: {n_comp}")
    model = PLSRegression(n_components=max_components, max_iter=500)
    model.fit(x_train, y_train)
    return model.predict(x_valid).ravel()


def evaluate_loso(
    feature_name: str,
    n_comp: int,
    x: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
) -> float:
    logo = LeaveOneGroupOut()
    oof = np.zeros(len(y), dtype=float)
    for train_idx, valid_idx in logo.split(x, y, groups):
        oof[valid_idx] = fit_predict(
            feature_name=feature_name,
            n_comp=n_comp,
            x_train=x[train_idx],
            y_train=y[train_idx],
            x_valid=x[valid_idx],
        )
    return rmse(y, oof)


def fit_full_model_predict(
    feature_name: str,
    n_comp: int,
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
) -> np.ndarray:
    return fit_predict(
        feature_name=feature_name,
        n_comp=n_comp,
        x_train=x_train,
        y_train=y_train,
        x_valid=x_test,
    )


def save_submission(
    sample_submit_df: pd.DataFrame,
    test_df: pd.DataFrame,
    preds: np.ndarray,
    feature_name: str,
    n_comp: int,
) -> Path:
    out_path = SUBMISSIONS_DIR / f"{EXPERIMENT_ID}_{feature_name}_n{n_comp}_submission.csv"
    pred_df = test_df[["sample_number"]].copy()
    pred_df["MC"] = preds
    submission_df = sample_submit_df[["sample_number"]].merge(
        pred_df,
        on="sample_number",
        how="left",
        validate="one_to_one",
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    submission_df.to_csv(out_path, index=False, header=False, encoding=DATA_ENCODING)
    return out_path


def main() -> None:
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)

    train_df, test_df, sample_submit_df = load_data()
    train_df = standardize_columns(train_df, is_train=True)
    test_df = standardize_columns(test_df, is_train=False)

    species_col = "species"
    target_col = "MC"
    wave_cols = wave_columns(train_df)

    x_features = build_feature_matrices(train_df, test_df, wave_cols)
    y = train_df[target_col].to_numpy(dtype=float)
    groups = train_df[species_col].to_numpy()

    results: list[dict[str, float | int | str]] = []
    for feature_name in FEATURES:
        x_train_feature, _ = x_features[feature_name]
        for n_comp in N_COMPONENTS_GRID:
            if feature_name.startswith("ratio_") and n_comp != 1:
                continue
            loso_rmse = evaluate_loso(feature_name, n_comp, x_train_feature, y, groups)
            results.append(
                {
                    "feature": feature_name,
                    "n_comp": n_comp,
                    "loso_rmse": loso_rmse,
                }
            )
            print(f"feature={feature_name} n_comp={n_comp} loso_rmse={loso_rmse:.6f}")

    results_df = pd.DataFrame(results).sort_values(["loso_rmse", "feature", "n_comp"]).reset_index(drop=True)
    results_path = EXPERIMENT_DIR / "results.csv"
    results_df.to_csv(results_path, index=False, encoding=DATA_ENCODING)
    print(f"saved_results={results_path}")

    best_row = results_df.iloc[0]
    best_feature = str(best_row["feature"])
    best_n_comp = int(best_row["n_comp"])
    print(f"best_feature={best_feature} best_n_comp={best_n_comp} best_loso_rmse={best_row['loso_rmse']:.6f}")

    x_train_best, x_test_best = x_features[best_feature]
    test_preds = fit_full_model_predict(best_feature, best_n_comp, x_train_best, y, x_test_best)
    negative_mask = test_preds < 0
    if np.any(negative_mask):
        negative_values = test_preds[negative_mask]
        print(f"negative_predictions_detected count={negative_mask.sum()} min={negative_values.min():.6f}")
        return

    submission_path = save_submission(sample_submit_df, test_df, test_preds, best_feature, best_n_comp)
    print(f"saved_submission={submission_path}")


if __name__ == "__main__":
    main()
