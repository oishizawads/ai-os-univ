from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"
SUBMISSIONS_DIR = PROJECT_ROOT / "submissions"

TRAIN_PATH = DATA_DIR / "train.csv"
TEST_PATH = DATA_DIR / "test.csv"
SAMPLE_SUBMIT_PATH = DATA_DIR / "sample_submit.csv"

TRAIN_ENCODING = "cp932"
TEST_ENCODING = "cp932"
SUBMIT_ENCODING = "cp932"

BAND1_RANGE = (6700.0, 7400.0)
BAND2_RANGE = (4800.0, 5350.0)

EXP_B001_PATH = SUBMISSIONS_DIR / "expB001_band2_snv_pls10_submission.csv"
EXP_B002_PATH = SUBMISSIONS_DIR / "expB002_band1band2_ensemble_submission.csv"
EXP_B003_PATH = SUBMISSIONS_DIR / "expB003_band2_snv_pls15_submission.csv"


def snv(x: np.ndarray) -> np.ndarray:
    row_mean = x.mean(axis=1, keepdims=True)
    row_std = x.std(axis=1, keepdims=True)
    return (x - row_mean) / np.clip(row_std, 1e-8, None)


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str], str, str]:
    train_df = pd.read_csv(TRAIN_PATH, encoding=TRAIN_ENCODING)
    test_df = pd.read_csv(TEST_PATH, encoding=TEST_ENCODING)
    sample_submit_df = pd.read_csv(
        SAMPLE_SUBMIT_PATH,
        header=None,
        names=["sample_number", "prediction"],
        encoding=SUBMIT_ENCODING,
    )

    sample_col = train_df.columns[0]
    target_col = train_df.columns[3]
    wave_cols = train_df.columns[4:].tolist()

    return train_df, test_df, sample_submit_df, wave_cols, sample_col, target_col


def select_band_columns(wave_cols: list[str], wn_range: tuple[float, float]) -> list[str]:
    wn = np.array([float(col) for col in wave_cols], dtype=np.float64)
    mask = (wn >= wn_range[0]) & (wn <= wn_range[1])
    selected = [col for col, keep in zip(wave_cols, mask) if keep]
    if not selected:
        raise ValueError(f"No wavelengths found in range {wn_range}.")
    return selected


def fit_predict_pls(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    n_components: int,
) -> np.ndarray:
    x_train = train_df[feature_cols].to_numpy(dtype=np.float64)
    y_train = train_df[target_col].to_numpy(dtype=np.float64)
    x_test = test_df[feature_cols].to_numpy(dtype=np.float64)

    x_train = snv(x_train)
    x_test = snv(x_test)

    model = PLSRegression(
        n_components=min(n_components, x_train.shape[0] - 1, x_train.shape[1]),
        max_iter=500,
    )
    model.fit(x_train, y_train)
    return model.predict(x_test).ravel().astype(np.float64)


def save_submission(
    sample_submit_df: pd.DataFrame,
    test_df: pd.DataFrame,
    sample_col: str,
    preds: np.ndarray,
    out_path: Path,
) -> pd.DataFrame:
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
        missing_ids = submission_df.loc[
            submission_df["prediction"].isna(), "sample_number"
        ].tolist()
        raise ValueError(f"Missing predictions for sample_number values: {missing_ids}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    submission_df.to_csv(out_path, index=False, header=False, encoding=SUBMIT_ENCODING)
    return submission_df


def print_prediction_stats(name: str, preds: np.ndarray, out_path: Path) -> None:
    print(f"[{name}]")
    print(f"saved_submission={out_path}")
    print(f"test_rows={len(preds)}")
    print(f"prediction_mean={preds.mean():.6f}")
    print(f"prediction_std={preds.std():.6f}")
    print(f"prediction_min={preds.min():.6f}")
    print(f"prediction_max={preds.max():.6f}")
    print("")


def main() -> None:
    train_df, test_df, sample_submit_df, wave_cols, sample_col, target_col = load_data()

    band1_cols = select_band_columns(wave_cols, BAND1_RANGE)
    band2_cols = select_band_columns(wave_cols, BAND2_RANGE)

    print(f"train_shape={train_df.shape}")
    print(f"test_shape={test_df.shape}")
    print(f"sample_submit_rows={len(sample_submit_df)}")
    print(f"band1_range_cm-1={BAND1_RANGE} band1_feature_count={len(band1_cols)}")
    print(f"band2_range_cm-1={BAND2_RANGE} band2_feature_count={len(band2_cols)}")
    print("")

    preds_b001 = fit_predict_pls(
        train_df=train_df,
        test_df=test_df,
        feature_cols=band2_cols,
        target_col=target_col,
        n_components=10,
    )
    save_submission(sample_submit_df, test_df, sample_col, preds_b001, EXP_B001_PATH)
    print_prediction_stats("expB001_band2_snv_pls10", preds_b001, EXP_B001_PATH)

    preds_band1 = fit_predict_pls(
        train_df=train_df,
        test_df=test_df,
        feature_cols=band1_cols,
        target_col=target_col,
        n_components=10,
    )
    preds_band2 = fit_predict_pls(
        train_df=train_df,
        test_df=test_df,
        feature_cols=band2_cols,
        target_col=target_col,
        n_components=10,
    )
    preds_b002 = (preds_band1 + preds_band2) / 2.0
    save_submission(sample_submit_df, test_df, sample_col, preds_b002, EXP_B002_PATH)
    print_prediction_stats(
        "expB002_band2_snv_pls10_band1_ensemble", preds_b002, EXP_B002_PATH
    )

    preds_b003 = fit_predict_pls(
        train_df=train_df,
        test_df=test_df,
        feature_cols=band2_cols,
        target_col=target_col,
        n_components=15,
    )
    save_submission(sample_submit_df, test_df, sample_col, preds_b003, EXP_B003_PATH)
    print_prediction_stats("expB003_band2_snv_pls15", preds_b003, EXP_B003_PATH)


if __name__ == "__main__":
    main()
