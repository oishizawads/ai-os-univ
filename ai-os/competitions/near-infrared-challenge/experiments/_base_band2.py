"""Shared utilities for band2 experiments."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw"
SUBMISSIONS_DIR = PROJECT_ROOT / "submissions"

TRAIN_PATH = DATA_DIR / "train.csv"
TEST_PATH = DATA_DIR / "test.csv"
SAMPLE_SUBMIT_PATH = DATA_DIR / "sample_submit.csv"

TRAIN_ENCODING = "cp932"
TEST_ENCODING = "cp932"
SUBMIT_ENCODING = "cp932"
BAND2_RANGE = (4800.0, 5350.0)
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
        SAMPLE_SUBMIT_PATH, header=None, names=["sample_number", "prediction"], encoding=SUBMIT_ENCODING
    )
    cols = train_df.columns.tolist()
    sample_col = pick_column(cols, ["sample_number", "sample number"], fallback_index=0)
    species_col = pick_column(cols, ["species", "樹種"], fallback_index=2)
    target_col = pick_column(cols, ["MC", "含水率"], fallback_index=3)
    wave_cols = [c for c in cols if is_float_column(c)]
    return train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col


def select_band2(wave_cols: list[str]) -> list[str]:
    wn = np.array([float(c) for c in wave_cols])
    mask = (wn >= BAND2_RANGE[0]) & (wn <= BAND2_RANGE[1])
    return [c for c, k in zip(wave_cols, mask) if k]


def apply_snv(X: np.ndarray) -> np.ndarray:
    mu = X.mean(axis=1, keepdims=True)
    sd = np.clip(X.std(axis=1, keepdims=True), EPS, None)
    return (X - mu) / sd


def apply_snv_sg1(X: np.ndarray) -> np.ndarray:
    return savgol_filter(apply_snv(X), window_length=11, polyorder=2, deriv=1, axis=1)


def loso_eval(X: np.ndarray, y: np.ndarray, groups: np.ndarray, model_fn, preproc_fn=None):
    """Run LOSO CV. model_fn(X_tr, y_tr) -> fitted model with .predict()"""
    logo = LeaveOneGroupOut()
    oof = np.zeros_like(y, dtype=np.float64)
    Xp = preproc_fn(X) if preproc_fn else X
    for fold, (tr, val) in enumerate(logo.split(Xp, y, groups), 1):
        m = model_fn(Xp[tr], y[tr])
        oof[val] = m.predict(Xp[val])
        holdout = np.unique(groups[val]).tolist()
        fold_rmse = float(np.sqrt(mean_squared_error(y[val], oof[val])))
        print(f"  fold={fold} holdout={holdout} rmse={fold_rmse:.4f}")
    rmse = float(np.sqrt(mean_squared_error(y, oof)))
    return rmse, oof


def save_submission(sample_submit_df, test_df, sample_col, preds, out_path):
    pred_df = pd.DataFrame({"sample_number": test_df[sample_col].to_numpy(), "prediction": preds})
    sub = sample_submit_df[["sample_number"]].merge(pred_df, on="sample_number", how="left", validate="one_to_one")
    if sub["prediction"].isna().any():
        raise ValueError("Missing predictions")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sub.to_csv(out_path, index=False, header=False, encoding=SUBMIT_ENCODING)
