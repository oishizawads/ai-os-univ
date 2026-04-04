from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

EXPERIMENT_ID = "expA008_deriv_ridge"
SEED = 42
N_FOLDS = 5
VALIDATION = "GroupKFold_species"
MODEL_NAME = "Ridge"
PREPROCESSING = "SavitzkyGolay_deriv1"
METRIC = "RMSE"
ALPHA = 1.0
DATA_ENCODING = "cp932"

ID_COL = "sample_number"
GROUP_COL = "species_number"
SPECIES_NAME_COL = "tree_species"
TARGET_COL = "moisture"
N_WAVE_FEATURES = 1555

SAVGOL_WINDOW = 11
SAVGOL_POLYORDER = 2
SAVGOL_DERIV = 1

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_DIR = PROJECT_ROOT / "experiments" / EXPERIMENT_ID
TRAIN_PATH = PROJECT_ROOT / "data" / "raw" / "train.csv"
TEST_PATH = PROJECT_ROOT / "data" / "raw" / "test.csv"
SAMPLE_SUBMIT_PATH = PROJECT_ROOT / "data" / "raw" / "sample_submit.csv"
MODEL_PATH = EXPERIMENT_DIR / "model.pkl"
OOF_PATH = EXPERIMENT_DIR / "oof.csv"
SUBMISSION_PATH = PROJECT_ROOT / "submissions" / f"{EXPERIMENT_ID}_submission.csv"


def apply_deriv(x: np.ndarray) -> np.ndarray:
    return savgol_filter(
        x,
        window_length=SAVGOL_WINDOW,
        polyorder=SAVGOL_POLYORDER,
        deriv=SAVGOL_DERIV,
        axis=1,
    )


def train_column_names() -> list[str]:
    return [ID_COL, GROUP_COL, SPECIES_NAME_COL, TARGET_COL] + [
        f"wave_{idx:04d}" for idx in range(1, N_WAVE_FEATURES + 1)
    ]


def test_column_names() -> list[str]:
    return [ID_COL, GROUP_COL, SPECIES_NAME_COL] + [
        f"wave_{idx:04d}" for idx in range(1, N_WAVE_FEATURES + 1)
    ]


def load_train_df() -> pd.DataFrame:
    df = pd.read_csv(TRAIN_PATH, encoding=DATA_ENCODING)
    df.columns = train_column_names()
    return df


def load_test_df() -> pd.DataFrame:
    df = pd.read_csv(TEST_PATH, encoding=DATA_ENCODING)
    df.columns = test_column_names()
    return df


def wave_columns() -> list[str]:
    return [f"wave_{idx:04d}" for idx in range(1, N_WAVE_FEATURES + 1)]
