from pathlib import Path

import numpy as np
from scipy.signal import savgol_filter

EXPERIMENT_ID = "expA006_deriv_corr_pls_top100"
SEED = 42
N_FOLDS = 5
VALIDATION = "GroupKFold_species"
MODEL_NAME = "PLSRegression"
PREPROCESSING = "SavitzkyGolay_deriv1"
METRIC = "RMSE"

N_TOP_FEATURES_CANDIDATES = [80, 90, 100, 110, 120, 140]
N_COMPONENTS_CANDIDATES = [8, 10, 12, 15, 18, 20]

SAVGOL_WINDOW = 11
SAVGOL_POLYORDER = 2
SAVGOL_DERIV = 1

DATA_ENCODING = "cp932"

ID_COL = "sample_number"
GROUP_COL = "species_number"
SPECIES_NAME_COL = "tree_species"
TARGET_COL = "moisture"
N_WAVE_FEATURES = 1555

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_DIR = PROJECT_ROOT / "experiments" / EXPERIMENT_ID
TRAIN_PATH = PROJECT_ROOT / "data" / "raw" / "train.csv"
TEST_PATH = PROJECT_ROOT / "data" / "raw" / "test.csv"
SAMPLE_SUBMIT_PATH = PROJECT_ROOT / "data" / "raw" / "sample_submit.csv"
MODEL_PATH = EXPERIMENT_DIR / "model.pkl"
OOF_PATH = EXPERIMENT_DIR / "oof.csv"
SUBMISSION_PATH = PROJECT_ROOT / "submissions" / f"{EXPERIMENT_ID}_submission.csv"


def apply_deriv(X: np.ndarray) -> np.ndarray:
    return savgol_filter(
        X,
        window_length=SAVGOL_WINDOW,
        polyorder=SAVGOL_POLYORDER,
        deriv=SAVGOL_DERIV,
        axis=1,
    )


def select_top_features(x: np.ndarray, y: np.ndarray, n_top: int) -> np.ndarray:
    x_c = x - x.mean(axis=0, keepdims=True)
    y_c = y - y.mean()
    std_x = x_c.std(axis=0)
    std_y = y_c.std()
    cov = (x_c * y_c[:, None]).mean(axis=0)
    corr = np.where(std_x > 0, cov / (std_x * std_y + 1e-12), 0.0)
    return np.argsort(np.abs(corr))[::-1][:n_top]


def train_column_names() -> list[str]:
    return [ID_COL, GROUP_COL, SPECIES_NAME_COL, TARGET_COL] + [
        f"wave_{idx:04d}" for idx in range(1, N_WAVE_FEATURES + 1)
    ]


def test_column_names() -> list[str]:
    return [ID_COL, GROUP_COL, SPECIES_NAME_COL] + [
        f"wave_{idx:04d}" for idx in range(1, N_WAVE_FEATURES + 1)
    ]


def load_train_df():
    import pandas as pd

    df = pd.read_csv(TRAIN_PATH, encoding=DATA_ENCODING)
    df.columns = train_column_names()
    return df


def load_test_df():
    import pandas as pd

    df = pd.read_csv(TEST_PATH, encoding=DATA_ENCODING)
    df.columns = test_column_names()
    return df


def wave_columns() -> list[str]:
    return [f"wave_{idx:04d}" for idx in range(1, N_WAVE_FEATURES + 1)]
