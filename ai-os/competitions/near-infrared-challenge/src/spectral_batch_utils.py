from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import detrend, savgol_filter
from sklearn.cross_decomposition import PLSRegression
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler

DATA_ENCODING = "cp932"
ID_COL = "sample_number"
GROUP_COL = "species_number"
SPECIES_NAME_COL = "tree_species"
TARGET_COL = "moisture"
N_WAVE_FEATURES = 1555


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def train_column_names() -> list[str]:
    return [ID_COL, GROUP_COL, SPECIES_NAME_COL, TARGET_COL] + [
        f"wave_{idx:04d}" for idx in range(1, N_WAVE_FEATURES + 1)
    ]


def test_column_names() -> list[str]:
    return [ID_COL, GROUP_COL, SPECIES_NAME_COL] + [
        f"wave_{idx:04d}" for idx in range(1, N_WAVE_FEATURES + 1)
    ]


def wave_columns() -> list[str]:
    return [f"wave_{idx:04d}" for idx in range(1, N_WAVE_FEATURES + 1)]


def load_train_df(project_root: Path) -> pd.DataFrame:
    df = pd.read_csv(project_root / "data" / "raw" / "train.csv", encoding=DATA_ENCODING)
    df.columns = train_column_names()
    return df


def load_test_df(project_root: Path) -> pd.DataFrame:
    df = pd.read_csv(project_root / "data" / "raw" / "test.csv", encoding=DATA_ENCODING)
    df.columns = test_column_names()
    return df


def load_sample_submit(project_root: Path) -> pd.DataFrame:
    return pd.read_csv(
        project_root / "data" / "raw" / "sample_submit.csv",
        header=None,
        names=[ID_COL, TARGET_COL],
        encoding=DATA_ENCODING,
    )


def apply_snv(x: np.ndarray) -> np.ndarray:
    row_mean = x.mean(axis=1, keepdims=True)
    row_std = x.std(axis=1, keepdims=True)
    return (x - row_mean) / np.clip(row_std, 1e-8, None)


def apply_msc(x: np.ndarray) -> np.ndarray:
    ref = x.mean(axis=0)
    corrected = np.empty_like(x)
    for i, row in enumerate(x):
        slope, intercept = np.polyfit(ref, row, 1)
        corrected[i] = (row - intercept) / max(slope, 1e-8)
    return corrected


def apply_sg(x: np.ndarray, window_length: int = 11, polyorder: int = 2, deriv: int = 1) -> np.ndarray:
    return savgol_filter(
        x,
        window_length=window_length,
        polyorder=polyorder,
        deriv=deriv,
        axis=1,
    )


def apply_detrending(x: np.ndarray) -> np.ndarray:
    return detrend(x, axis=1, type="linear")


def top_corr_indices(x: np.ndarray, y: np.ndarray, n_top: int) -> np.ndarray:
    x_c = x - x.mean(axis=0, keepdims=True)
    y_c = y - y.mean()
    std_x = x_c.std(axis=0)
    std_y = y_c.std()
    cov = (x_c * y_c[:, None]).mean(axis=0)
    corr = np.where(std_x > 0, cov / (std_x * std_y + 1e-12), 0.0)
    return np.argsort(np.abs(corr))[::-1][:n_top]


def vip_scores(pls: PLSRegression, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    t = pls.x_scores_
    w = pls.x_weights_
    q = pls.y_loadings_
    p, h = w.shape
    s = np.diag(t.T @ t @ q.T @ q).reshape(h, -1)
    total_s = np.sum(s)
    if total_s <= 0:
        return np.ones(p)
    vips = np.zeros(p)
    for i in range(p):
        weight = np.array([(w[i, j] ** 2) / np.sum(w[:, j] ** 2) for j in range(h)])
        vips[i] = math.sqrt(p * np.sum(s.flatten() * weight) / total_s)
    return vips


def candidate_interval_masks(n_features: int, n_intervals: int, pick_sizes: list[int]) -> list[np.ndarray]:
    interval_size = n_features // n_intervals
    masks: list[np.ndarray] = []
    for pick_size in pick_sizes:
        for start in range(0, n_intervals - pick_size + 1):
            mask = np.zeros(n_features, dtype=bool)
            left = start * interval_size
            right = n_features if start + pick_size == n_intervals else (start + pick_size) * interval_size
            mask[left:right] = True
            masks.append(mask)
    return masks


@dataclass
class ExperimentResult:
    experiment_id: str
    theme: str
    validation: str
    best_params: dict
    oof_rmse: float
    fold_rmse_mean: float
    fold_rmse_std: float
    output_path: Path | None = None
    submission_path: Path | None = None


def save_submission(
    project_root: Path,
    preds: np.ndarray,
    out_path: Path,
) -> None:
    test_df = load_test_df(project_root)
    test_df[TARGET_COL] = preds
    submission_df = load_sample_submit(project_root)
    pred_df = test_df[[ID_COL, TARGET_COL]].copy()
    submission_df = submission_df[[ID_COL]].merge(pred_df, on=ID_COL, how="left", validate="one_to_one")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    submission_df.to_csv(out_path, index=False, header=False)


def evaluate_group_model(
    x: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    fit_predict_fn,
) -> tuple[float, list[float], np.ndarray]:
    splitter = GroupKFold(n_splits=5)
    oof = np.zeros(len(y), dtype=float)
    fold_scores: list[float] = []
    for train_idx, valid_idx in splitter.split(x, y, groups):
        valid_pred = fit_predict_fn(x[train_idx], y[train_idx], x[valid_idx], groups[train_idx])
        oof[valid_idx] = valid_pred
        fold_scores.append(rmse(y[valid_idx], valid_pred))
    return rmse(y, oof), fold_scores, oof


def evaluate_logo_model(
    x: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    fit_predict_fn,
) -> tuple[float, list[float], np.ndarray]:
    splitter = LeaveOneGroupOut()
    oof = np.zeros(len(y), dtype=float)
    fold_scores: list[float] = []
    for train_idx, valid_idx in splitter.split(x, y, groups):
        valid_pred = fit_predict_fn(x[train_idx], y[train_idx], x[valid_idx], groups[train_idx])
        oof[valid_idx] = valid_pred
        fold_scores.append(rmse(y[valid_idx], valid_pred))
    return rmse(y, oof), fold_scores, oof


def fit_pls_predict(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_valid: np.ndarray,
    n_components: int,
) -> np.ndarray:
    model = PLSRegression(n_components=n_components, max_iter=500)
    model.fit(x_train, y_train)
    return model.predict(x_valid).ravel()


def fit_elastic_predict(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_valid: np.ndarray,
    alpha: float,
    l1_ratio: float,
) -> np.ndarray:
    scaler = StandardScaler()
    x_train_s = scaler.fit_transform(x_train)
    x_valid_s = scaler.transform(x_valid)
    model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, max_iter=5000, random_state=42)
    model.fit(x_train_s, y_train)
    return model.predict(x_valid_s)
