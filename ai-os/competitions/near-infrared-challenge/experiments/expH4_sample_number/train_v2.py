from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GroupKFold

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAIN_PATH = PROJECT_ROOT / "data" / "raw" / "train.csv"
TEST_PATH = PROJECT_ROOT / "data" / "raw" / "test.csv"
SAMPLE_SUBMIT_PATH = PROJECT_ROOT / "data" / "raw" / "sample_submit.csv"
SUBMISSION_PATH = PROJECT_ROOT / "submissions" / "expH4b_refined_submission.csv"
ENCODING = "cp932"

ID_COL = "sample number"
SPECIES_COL = "species number"
NEIGHBOR_COUNT = 3
N_SPLITS = 5
PLS_COMPONENTS = 15
EPS = 1e-6


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, list[str], str]:
    train_df = pd.read_csv(TRAIN_PATH, encoding=ENCODING)
    test_df = pd.read_csv(TEST_PATH, encoding=ENCODING)
    target_col = train_df.columns[3]
    wave_cols = train_df.columns[4:].tolist()
    return train_df, test_df, wave_cols, target_col


def build_species_summary(df: pd.DataFrame, target_col: str | None = None) -> pd.DataFrame:
    agg_map: dict[str, tuple[str, str]] = {
        "sample_min": (ID_COL, "min"),
        "sample_max": (ID_COL, "max"),
        "sample_mean": (ID_COL, "mean"),
        "n_samples": (ID_COL, "size"),
    }
    if target_col is not None:
        agg_map["target_min"] = (target_col, "min")
        agg_map["target_max"] = (target_col, "max")
        agg_map["target_mean"] = (target_col, "mean")

    return (
        df.groupby(SPECIES_COL, sort=True)
        .agg(**agg_map)
        .reset_index()
        .sort_values(["sample_min", SPECIES_COL])
        .reset_index(drop=True)
    )


def distance_between_ranges(
    left_min: float, left_max: float, right_min: float, right_max: float
) -> float:
    if left_max < right_min:
        return float(right_min - left_max)
    if right_max < left_min:
        return float(left_min - right_max)
    return 0.0


def get_neighbor_rows(
    target_min: float,
    target_max: float,
    candidate_summary: pd.DataFrame,
    n_neighbors: int = NEIGHBOR_COUNT,
) -> list[dict[str, float]]:
    target_mid = (target_min + target_max) / 2.0
    ranked: list[dict[str, float]] = []
    for row in candidate_summary.itertuples(index=False):
        dist = distance_between_ranges(target_min, target_max, row.sample_min, row.sample_max)
        midpoint_gap = abs(((row.sample_min + row.sample_max) / 2.0) - target_mid)
        ranked.append(
            {
                "species": int(row[0]),
                "distance": float(dist),
                "midpoint_gap": float(midpoint_gap),
            }
        )

    ranked.sort(key=lambda x: (x["distance"], x["midpoint_gap"], x["species"]))
    return ranked[:n_neighbors]


def neighbor_weights(neighbors: list[dict[str, float]]) -> np.ndarray:
    distances = np.array([item["distance"] for item in neighbors], dtype=np.float64)
    zero_mask = distances <= EPS
    if zero_mask.any():
        weights = zero_mask.astype(np.float64)
    else:
        weights = 1.0 / (distances + EPS)
    return weights / weights.sum()


def fit_pls(
    train_df: pd.DataFrame, wave_cols: list[str], target_col: str, n_components: int = PLS_COMPONENTS
) -> PLSRegression:
    model = PLSRegression(n_components=n_components, max_iter=500)
    model.fit(
        train_df[wave_cols].to_numpy(dtype=np.float64),
        train_df[target_col].to_numpy(dtype=np.float64),
    )
    return model


def predict_pls(model: PLSRegression, df: pd.DataFrame, wave_cols: list[str]) -> np.ndarray:
    return model.predict(df[wave_cols].to_numpy(dtype=np.float64)).ravel()


def compute_residual_models(
    train_df: pd.DataFrame,
    y_pls_train: np.ndarray,
    target_col: str,
) -> pd.DataFrame:
    rows: list[dict[str, float | int]] = []
    temp = train_df[[SPECIES_COL, ID_COL, target_col]].copy()
    temp["y_pls"] = y_pls_train
    temp["residual"] = temp[target_col] - temp["y_pls"]

    for species, part in temp.groupby(SPECIES_COL, sort=True):
        reg = LinearRegression()
        x = part[[ID_COL]].to_numpy(dtype=np.float64)
        y = part["residual"].to_numpy(dtype=np.float64)
        reg.fit(x, y)
        rows.append(
            {
                SPECIES_COL: int(species),
                "residual_slope": float(reg.coef_[0]),
                "residual_intercept": float(reg.intercept_),
                "sample_mean": float(part[ID_COL].mean()),
                "residual_mean": float(part["residual"].mean()),
            }
        )

    return pd.DataFrame(rows).sort_values(SPECIES_COL).reset_index(drop=True)


def compute_species_line_models(train_df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    rows: list[dict[str, float | int]] = []
    for species, part in train_df.groupby(SPECIES_COL, sort=True):
        reg = LinearRegression()
        x = part[[ID_COL]].to_numpy(dtype=np.float64)
        y = part[target_col].to_numpy(dtype=np.float64)
        reg.fit(x, y)
        rows.append(
            {
                SPECIES_COL: int(species),
                "line_slope": float(reg.coef_[0]),
                "line_intercept": float(reg.intercept_),
                "sample_min": float(part[ID_COL].min()),
                "sample_max": float(part[ID_COL].max()),
            }
        )
    return pd.DataFrame(rows).sort_values(SPECIES_COL).reset_index(drop=True)


def predict_model_d(
    fit_df: pd.DataFrame,
    target_df: pd.DataFrame,
    wave_cols: list[str],
    target_col: str,
    n_neighbors: int = NEIGHBOR_COUNT,
) -> tuple[np.ndarray, dict[int, list[int]], pd.DataFrame]:
    pls_model = fit_pls(fit_df, wave_cols, target_col)
    y_pls_fit = predict_pls(pls_model, fit_df, wave_cols)
    y_pls_target = predict_pls(pls_model, target_df, wave_cols)
    residual_df = compute_residual_models(fit_df, y_pls_fit, target_col)
    residual_lookup = residual_df.set_index(SPECIES_COL)
    fit_summary = build_species_summary(fit_df, target_col=target_col)
    target_summary = build_species_summary(target_df)

    preds = y_pls_target.copy()
    neighbor_map: dict[int, list[int]] = {}

    for row in target_summary.itertuples(index=False):
        species = int(row[0])
        neighbors = get_neighbor_rows(
            target_min=float(row.sample_min),
            target_max=float(row.sample_max),
            candidate_summary=fit_summary,
            n_neighbors=n_neighbors,
        )
        weights = neighbor_weights(neighbors)
        neighbor_species = [item["species"] for item in neighbors]
        neighbor_map[species] = neighbor_species

        slope_values = residual_lookup.loc[neighbor_species, "residual_slope"].to_numpy(dtype=np.float64)
        test_slope = float(np.dot(weights, slope_values))

        mask = target_df[SPECIES_COL] == species
        sample_values = target_df.loc[mask, ID_COL].to_numpy(dtype=np.float64)
        sample_mean = float(sample_values.mean())
        preds[mask.to_numpy()] = y_pls_target[mask.to_numpy()] + test_slope * (sample_values - sample_mean)

    return preds, neighbor_map, residual_df


def rescale_values(values: np.ndarray, target_start: float, target_end: float) -> np.ndarray:
    if len(values) == 1:
        return np.array([(target_start + target_end) / 2.0], dtype=np.float64)

    src_min = float(np.min(values))
    src_max = float(np.max(values))
    if abs(src_max - src_min) <= EPS:
        return np.linspace(target_start, target_end, len(values), dtype=np.float64)
    scaled = (values - src_min) / (src_max - src_min)
    return target_start + scaled * (target_end - target_start)


def predict_model_e(
    fit_df: pd.DataFrame,
    target_df: pd.DataFrame,
    wave_cols: list[str],
    target_col: str,
    n_neighbors: int = NEIGHBOR_COUNT,
) -> tuple[np.ndarray, dict[int, list[int]], pd.DataFrame]:
    pls_model = fit_pls(fit_df, wave_cols, target_col)
    y_pls_target = predict_pls(pls_model, target_df, wave_cols)
    fit_summary = build_species_summary(fit_df, target_col=target_col)
    target_summary = build_species_summary(target_df)
    line_df = compute_species_line_models(fit_df, target_col)
    line_lookup = line_df.set_index(SPECIES_COL)

    preds = np.zeros(len(target_df), dtype=np.float64)
    neighbor_map: dict[int, list[int]] = {}

    for row in target_summary.itertuples(index=False):
        species = int(row[0])
        neighbors = get_neighbor_rows(
            target_min=float(row.sample_min),
            target_max=float(row.sample_max),
            candidate_summary=fit_summary,
            n_neighbors=n_neighbors,
        )
        weights = neighbor_weights(neighbors)
        neighbor_species = [item["species"] for item in neighbors]
        neighbor_map[species] = neighbor_species

        slopes = line_lookup.loc[neighbor_species, "line_slope"].to_numpy(dtype=np.float64)
        intercepts = line_lookup.loc[neighbor_species, "line_intercept"].to_numpy(dtype=np.float64)
        weighted_slope = float(np.dot(weights, slopes))
        weighted_intercept = float(np.dot(weights, intercepts))

        mask = target_df[SPECIES_COL] == species
        target_positions = np.flatnonzero(mask.to_numpy())
        local_df = target_df.loc[mask, [ID_COL]].copy()
        local_df["local_pos"] = np.arange(len(local_df), dtype=np.int64)
        local_df["y_pls"] = y_pls_target[mask.to_numpy()]
        local_df = local_df.sort_values(ID_COL).reset_index(drop=True)

        pred_at_min = weighted_intercept + weighted_slope * float(local_df[ID_COL].min())
        pred_at_max = weighted_intercept + weighted_slope * float(local_df[ID_COL].max())

        y_sorted = np.sort(local_df["y_pls"].to_numpy(dtype=np.float64))
        if pred_at_min >= pred_at_max:
            ordered = y_sorted[::-1]
        else:
            ordered = y_sorted

        scaled = rescale_values(ordered, pred_at_min, pred_at_max)
        preds[target_positions[local_df["local_pos"].to_numpy(dtype=np.int64)]] = scaled

    return preds, neighbor_map, line_df


def cross_validate(
    train_df: pd.DataFrame,
    wave_cols: list[str],
    target_col: str,
) -> dict[str, object]:
    groups = train_df[SPECIES_COL].to_numpy()
    y = train_df[target_col].to_numpy(dtype=np.float64)
    gkf = GroupKFold(n_splits=N_SPLITS)

    oof_pls = np.zeros(len(train_df), dtype=np.float64)
    oof_d = np.zeros(len(train_df), dtype=np.float64)
    oof_e = np.zeros(len(train_df), dtype=np.float64)

    fold_rows: list[dict[str, float | int]] = []

    for fold, (fit_idx, valid_idx) in enumerate(gkf.split(train_df, y, groups), start=1):
        fit_df = train_df.iloc[fit_idx].copy()
        valid_df = train_df.iloc[valid_idx].copy()

        pls_model = fit_pls(fit_df, wave_cols, target_col)
        valid_pls = predict_pls(pls_model, valid_df, wave_cols)
        valid_d, _, _ = predict_model_d(fit_df, valid_df, wave_cols, target_col)
        valid_e, _, _ = predict_model_e(fit_df, valid_df, wave_cols, target_col)

        oof_pls[valid_idx] = valid_pls
        oof_d[valid_idx] = valid_d
        oof_e[valid_idx] = valid_e

        y_valid = y[valid_idx]
        fold_rows.append(
            {
                "fold": fold,
                "n_valid": len(valid_idx),
                "rmse_pls": rmse(y_valid, valid_pls),
                "rmse_d": rmse(y_valid, valid_d),
                "rmse_e": rmse(y_valid, valid_e),
            }
        )

    fold_df = pd.DataFrame(fold_rows)
    return {
        "fold_df": fold_df,
        "oof_pls": oof_pls,
        "oof_d": oof_d,
        "oof_e": oof_e,
        "rmse_pls": rmse(y, oof_pls),
        "rmse_d": rmse(y, oof_d),
        "rmse_e": rmse(y, oof_e),
    }


def summarize_predictions(pred: np.ndarray) -> pd.Series:
    return pd.Series(
        {
            "mean": float(np.mean(pred)),
            "std": float(np.std(pred)),
            "min": float(np.min(pred)),
            "max": float(np.max(pred)),
        }
    )


def species_prediction_stats(test_df: pd.DataFrame, pred: np.ndarray) -> pd.DataFrame:
    temp = test_df[[SPECIES_COL, ID_COL]].copy()
    temp["prediction"] = pred
    return (
        temp.groupby(SPECIES_COL, sort=True)
        .agg(
            sample_min=(ID_COL, "min"),
            sample_max=(ID_COL, "max"),
            n_samples=(ID_COL, "size"),
            pred_mean=("prediction", "mean"),
            pred_std=("prediction", "std"),
            pred_min=("prediction", "min"),
            pred_max=("prediction", "max"),
        )
        .reset_index()
    )


def save_submission(test_df: pd.DataFrame, pred: np.ndarray) -> None:
    sample_submit = pd.read_csv(SAMPLE_SUBMIT_PATH, encoding=ENCODING)
    submit_cols = sample_submit.columns.tolist()
    submission = pd.DataFrame(
        {
            submit_cols[0]: test_df[ID_COL].to_numpy(),
            submit_cols[1]: pred,
        }
    )
    SUBMISSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    submission.to_csv(SUBMISSION_PATH, index=False, encoding=ENCODING)


def main() -> None:
    train_df, test_df, wave_cols, target_col = load_data()

    print(f"train_shape={train_df.shape}")
    print(f"test_shape={test_df.shape}")
    print(f"target_col={target_col}")
    print(f"n_wave_cols={len(wave_cols)}")
    print(f"groupkfold_splits={N_SPLITS}")
    print(f"pls_components={PLS_COMPONENTS}")
    print("")

    cv = cross_validate(train_df, wave_cols, target_col)
    fold_df = cv["fold_df"]

    print("[GroupKFold fold RMSE]")
    print(fold_df.to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print("")

    print("[OOF RMSE summary]")
    print(f"PLS_only_rmse={cv['rmse_pls']:.6f}")
    print(f"ModelD_rmse={cv['rmse_d']:.6f}")
    print(f"ModelE_rmse={cv['rmse_e']:.6f}")
    print(f"PLS_fold_mean={fold_df['rmse_pls'].mean():.6f}")
    print(f"PLS_fold_std={fold_df['rmse_pls'].std(ddof=0):.6f}")
    print(f"ModelD_fold_mean={fold_df['rmse_d'].mean():.6f}")
    print(f"ModelD_fold_std={fold_df['rmse_d'].std(ddof=0):.6f}")
    print(f"ModelE_fold_mean={fold_df['rmse_e'].mean():.6f}")
    print(f"ModelE_fold_std={fold_df['rmse_e'].std(ddof=0):.6f}")
    print("")

    pls_model = fit_pls(train_df, wave_cols, target_col)
    test_pred_pls = predict_pls(pls_model, test_df, wave_cols)
    test_pred_d, test_neighbors_d, residual_df = predict_model_d(train_df, test_df, wave_cols, target_col)
    test_pred_e, test_neighbors_e, line_df = predict_model_e(train_df, test_df, wave_cols, target_col)

    print("[PLS only test stats]")
    print(summarize_predictions(test_pred_pls).to_string(float_format=lambda x: f"{x:.6f}"))
    print("[PLS only species stats]")
    print(species_prediction_stats(test_df, test_pred_pls).to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print("")

    print("[Model D residual slopes]")
    print(residual_df.to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print("test_neighbors_model_d=", test_neighbors_d)
    print("[Model D test stats]")
    print(summarize_predictions(test_pred_d).to_string(float_format=lambda x: f"{x:.6f}"))
    print("[Model D species stats]")
    print(species_prediction_stats(test_df, test_pred_d).to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print("")

    print("[Model E species line models]")
    print(line_df.to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print("test_neighbors_model_e=", test_neighbors_e)
    print("[Model E test stats]")
    print(summarize_predictions(test_pred_e).to_string(float_format=lambda x: f"{x:.6f}"))
    print("[Model E species stats]")
    print(species_prediction_stats(test_df, test_pred_e).to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print("")

    candidates = [
        ("PLS_only", cv["rmse_pls"], test_pred_pls),
        ("ModelD", cv["rmse_d"], test_pred_d),
        ("ModelE", cv["rmse_e"], test_pred_e),
    ]
    best_name, best_rmse, best_pred = min(candidates, key=lambda x: float(x[1]))

    save_submission(test_df, best_pred)
    print("[Model selection]")
    print(f"best_model={best_name}")
    print(f"best_oof_rmse={best_rmse:.6f}")
    print(f"submission_path={SUBMISSION_PATH}")


if __name__ == "__main__":
    main()
