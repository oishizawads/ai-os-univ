from pathlib import Path

import pandas as pd

EXPERIMENT_ID = "expA003_pls"
SEED = 42
N_FOLDS = 5
VALIDATION = "KFold_5"
MODEL_NAME = "PLSRegression"
PREPROCESSING = "raw"
METRIC = "RMSE"
N_COMPONENTS_CANDIDATES = [5, 10, 15, 20, 25, 30, 40, 50]
DATA_ENCODING = "cp932"

ID_COL = "sample_number"
RAW_SPECIES_NUMBER_COL = "species_number"
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


def train_column_names() -> list[str]:
    return [ID_COL, RAW_SPECIES_NUMBER_COL, SPECIES_NAME_COL, TARGET_COL] + [
        f"wave_{idx:04d}" for idx in range(1, N_WAVE_FEATURES + 1)
    ]


def test_column_names() -> list[str]:
    return [ID_COL, RAW_SPECIES_NUMBER_COL, SPECIES_NAME_COL] + [
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
