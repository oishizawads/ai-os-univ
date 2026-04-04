from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAIN_PATH = PROJECT_ROOT / "data" / "raw" / "train.csv"
TEST_PATH = PROJECT_ROOT / "data" / "raw" / "test.csv"
SAMPLE_SUBMIT_PATH = PROJECT_ROOT / "data" / "raw" / "sample_submit.csv"
SUBMISSION_PATH = PROJECT_ROOT / "submissions" / "expH4_sample_number_submission.csv"
ENCODING = "cp932"

ID_COL = "sample number"
SPECIES_COL = "species number"


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
        "n_samples": (ID_COL, "size"),
        "sample_mean": (ID_COL, "mean"),
    }
    if target_col is not None:
        agg_map["target_min"] = (target_col, "min")
        agg_map["target_max"] = (target_col, "max")
        agg_map["target_mean"] = (target_col, "mean")

    summary = (
        df.groupby(SPECIES_COL, sort=True)
        .agg(**agg_map)
        .reset_index()
        .sort_values("sample_min")
        .reset_index(drop=True)
    )
    return summary


def distance_between_ranges(
    left_min: float, left_max: float, right_min: float, right_max: float
) -> float:
    if left_max < right_min:
        return float(right_min - left_max)
    if right_max < left_min:
        return float(left_min - right_max)
    return 0.0


def select_neighbor_species(
    target_min: float,
    target_max: float,
    candidate_summary: pd.DataFrame,
    max_neighbors: int = 4,
) -> list[int]:
    ranked: list[tuple[float, float, int]] = []
    target_mid = (target_min + target_max) / 2.0

    for row in candidate_summary.itertuples(index=False):
        dist = distance_between_ranges(target_min, target_max, row.sample_min, row.sample_max)
        candidate_mid = (row.sample_min + row.sample_max) / 2.0
        midpoint_gap = abs(candidate_mid - target_mid)
        ranked.append((dist, midpoint_gap, int(row[0])))

    ranked.sort()
    selected = [species for _, _, species in ranked[:max_neighbors]]
    return selected


def predict_model_a(
    train_df: pd.DataFrame, test_df: pd.DataFrame, target_col: str
) -> tuple[np.ndarray, np.ndarray, LinearRegression]:
    model = LinearRegression()
    x_train = train_df[[ID_COL]].to_numpy(dtype=np.float64)
    y_train = train_df[target_col].to_numpy(dtype=np.float64)
    x_test = test_df[[ID_COL]].to_numpy(dtype=np.float64)

    logo = LeaveOneGroupOut()
    groups = train_df[SPECIES_COL].to_numpy()
    oof = np.zeros(len(train_df), dtype=np.float64)

    for fit_idx, valid_idx in logo.split(x_train, y_train, groups):
        fold_model = LinearRegression()
        fold_model.fit(x_train[fit_idx], y_train[fit_idx])
        oof[valid_idx] = fold_model.predict(x_train[valid_idx])

    model.fit(x_train, y_train)
    test_pred = model.predict(x_test)
    return oof, test_pred, model


def predict_model_b(
    train_df: pd.DataFrame,
    target_df: pd.DataFrame,
    train_summary: pd.DataFrame,
    target_summary: pd.DataFrame,
    target_col: str,
    max_neighbors: int = 4,
) -> tuple[np.ndarray, dict[int, list[int]]]:
    preds = np.zeros(len(target_df), dtype=np.float64)
    neighbor_map: dict[int, list[int]] = {}

    for row in target_summary.itertuples(index=False):
        species = int(row[0])
        neighbors = select_neighbor_species(
            target_min=float(row.sample_min),
            target_max=float(row.sample_max),
            candidate_summary=train_summary,
            max_neighbors=max_neighbors,
        )
        neighbor_map[species] = neighbors

        fit_df = train_df[train_df[SPECIES_COL].isin(neighbors)]
        pred_mask = target_df[SPECIES_COL] == species

        model = LinearRegression()
        model.fit(
            fit_df[[ID_COL]].to_numpy(dtype=np.float64),
            fit_df[target_col].to_numpy(dtype=np.float64),
        )
        preds[pred_mask.to_numpy()] = model.predict(
            target_df.loc[pred_mask, [ID_COL]].to_numpy(dtype=np.float64)
        )

    return preds, neighbor_map


def compute_species_slopes(train_df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    rows: list[dict[str, float | int]] = []
    for species, part in train_df.groupby(SPECIES_COL, sort=True):
        model = LinearRegression()
        x = part[[ID_COL]].to_numpy(dtype=np.float64)
        y = part[target_col].to_numpy(dtype=np.float64)
        model.fit(x, y)
        rows.append(
            {
                SPECIES_COL: int(species),
                "slope": float(model.coef_[0]),
                "sample_mean": float(part[ID_COL].mean()),
                "target_mean": float(part[target_col].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values(SPECIES_COL).reset_index(drop=True)


def fit_pls_predict(
    train_df: pd.DataFrame,
    target_df: pd.DataFrame,
    wave_cols: list[str],
    target_col: str,
    n_components: int = 15,
) -> np.ndarray:
    model = PLSRegression(n_components=n_components, max_iter=500)
    model.fit(
        train_df[wave_cols].to_numpy(dtype=np.float64),
        train_df[target_col].to_numpy(dtype=np.float64),
    )
    pred = model.predict(target_df[wave_cols].to_numpy(dtype=np.float64)).ravel()
    return pred


def predict_model_c(
    train_df: pd.DataFrame,
    target_df: pd.DataFrame,
    wave_cols: list[str],
    target_col: str,
    train_summary: pd.DataFrame,
    target_summary: pd.DataFrame,
    max_neighbors: int = 4,
) -> tuple[np.ndarray, dict[int, list[int]], pd.DataFrame]:
    y_spec = fit_pls_predict(train_df, target_df, wave_cols, target_col, n_components=15)
    preds = y_spec.copy()
    neighbor_map: dict[int, list[int]] = {}
    slope_df = compute_species_slopes(train_df, target_col)
    slope_lookup = slope_df.set_index(SPECIES_COL)

    for row in target_summary.itertuples(index=False):
        species = int(row[0])
        neighbors = select_neighbor_species(
            target_min=float(row.sample_min),
            target_max=float(row.sample_max),
            candidate_summary=train_summary,
            max_neighbors=max_neighbors,
        )
        neighbor_map[species] = neighbors

        mean_slope = float(slope_lookup.loc[neighbors, "slope"].mean())
        sample_anchor = float(slope_lookup.loc[neighbors, "sample_mean"].mean())
        pred_mask = target_df[SPECIES_COL] == species
        centered_sample = (
            target_df.loc[pred_mask, ID_COL].to_numpy(dtype=np.float64) - sample_anchor
        )
        preds[pred_mask.to_numpy()] = y_spec[pred_mask.to_numpy()] + mean_slope * centered_sample

    return preds, neighbor_map, slope_df


def evaluate_model_a_loso(train_df: pd.DataFrame, target_col: str) -> tuple[float, np.ndarray]:
    oof, _, _ = predict_model_a(train_df, train_df, target_col)
    return rmse(train_df[target_col].to_numpy(dtype=np.float64), oof), oof


def evaluate_model_b_loso(
    train_df: pd.DataFrame, target_col: str, max_neighbors: int = 4
) -> tuple[float, np.ndarray, dict[int, list[int]]]:
    logo = LeaveOneGroupOut()
    groups = train_df[SPECIES_COL].to_numpy()
    y = train_df[target_col].to_numpy(dtype=np.float64)
    oof = np.zeros(len(train_df), dtype=np.float64)
    all_neighbors: dict[int, list[int]] = {}

    for fit_idx, valid_idx in logo.split(train_df, y, groups):
        fit_df = train_df.iloc[fit_idx].copy()
        valid_df = train_df.iloc[valid_idx].copy()
        fit_summary = build_species_summary(fit_df, target_col=target_col)
        valid_summary = build_species_summary(valid_df, target_col=target_col)
        valid_pred, fold_neighbors = predict_model_b(
            train_df=fit_df,
            target_df=valid_df,
            train_summary=fit_summary,
            target_summary=valid_summary,
            target_col=target_col,
            max_neighbors=max_neighbors,
        )
        oof[valid_idx] = valid_pred
        all_neighbors.update(fold_neighbors)

    return rmse(y, oof), oof, all_neighbors


def evaluate_model_c_loso(
    train_df: pd.DataFrame,
    wave_cols: list[str],
    target_col: str,
    max_neighbors: int = 4,
) -> tuple[float, np.ndarray, dict[int, list[int]]]:
    logo = LeaveOneGroupOut()
    groups = train_df[SPECIES_COL].to_numpy()
    y = train_df[target_col].to_numpy(dtype=np.float64)
    oof = np.zeros(len(train_df), dtype=np.float64)
    all_neighbors: dict[int, list[int]] = {}

    for fit_idx, valid_idx in logo.split(train_df, y, groups):
        fit_df = train_df.iloc[fit_idx].copy()
        valid_df = train_df.iloc[valid_idx].copy()
        fit_summary = build_species_summary(fit_df, target_col=target_col)
        valid_summary = build_species_summary(valid_df, target_col=target_col)
        valid_pred, fold_neighbors, _ = predict_model_c(
            train_df=fit_df,
            target_df=valid_df,
            wave_cols=wave_cols,
            target_col=target_col,
            train_summary=fit_summary,
            target_summary=valid_summary,
            max_neighbors=max_neighbors,
        )
        oof[valid_idx] = valid_pred
        all_neighbors.update(fold_neighbors)

    return rmse(y, oof), oof, all_neighbors


def summarize_predictions(pred: np.ndarray) -> dict[str, float]:
    return {
        "mean": float(np.mean(pred)),
        "std": float(np.std(pred)),
        "min": float(np.min(pred)),
        "max": float(np.max(pred)),
    }


def choose_best_model(results: list[dict[str, object]]) -> dict[str, object]:
    ranked = sorted(
        results,
        key=lambda row: (
            float(row["test_std"]),
            float(row["oof_rmse"]),
        ),
    )
    return ranked[0]


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
    print("")

    train_summary = build_species_summary(train_df, target_col=target_col)
    test_summary = build_species_summary(test_df)

    print("[Train species summary]")
    print(train_summary.to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print("")

    print("[Test species summary]")
    print(test_summary.to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print("")

    a_oof_rmse, _ = evaluate_model_a_loso(train_df, target_col)
    a_oof, a_test_pred, a_model = predict_model_a(train_df, test_df, target_col)
    print("[Model A] Global LinearRegression(sample_number -> moisture)")
    print(f"coef={float(a_model.coef_[0]):.6f}")
    print(f"intercept={float(a_model.intercept_):.6f}")
    print(f"loso_oof_rmse={a_oof_rmse:.6f}")
    print(pd.Series(summarize_predictions(a_test_pred)).to_string())
    print("")

    b_oof_rmse, _, b_oof_neighbors = evaluate_model_b_loso(train_df, target_col)
    b_test_pred, b_test_neighbors = predict_model_b(
        train_df=train_df,
        target_df=test_df,
        train_summary=train_summary,
        target_summary=test_summary,
        target_col=target_col,
    )
    print("[Model B] Neighbor species interpolation")
    print(f"loso_oof_rmse={b_oof_rmse:.6f}")
    print("train_loso_neighbors=", b_oof_neighbors)
    print("test_neighbors=", b_test_neighbors)
    print(pd.Series(summarize_predictions(b_test_pred)).to_string())
    print("")

    c_oof_rmse, _, c_oof_neighbors = evaluate_model_c_loso(train_df, wave_cols, target_col)
    c_test_pred, c_test_neighbors, slope_df = predict_model_c(
        train_df=train_df,
        target_df=test_df,
        wave_cols=wave_cols,
        target_col=target_col,
        train_summary=train_summary,
        target_summary=test_summary,
    )
    print("[Model C] PLS + neighbor slope correction")
    print(f"loso_oof_rmse={c_oof_rmse:.6f}")
    print("[Species slopes]")
    print(slope_df.to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print("train_loso_neighbors=", c_oof_neighbors)
    print("test_neighbors=", c_test_neighbors)
    print(pd.Series(summarize_predictions(c_test_pred)).to_string())
    print("")

    results: list[dict[str, object]] = [
        {
            "model_name": "A_global_linear",
            "oof_rmse": a_oof_rmse,
            "test_std": summarize_predictions(a_test_pred)["std"],
            "test_pred": a_test_pred,
        },
        {
            "model_name": "B_neighbor_interp",
            "oof_rmse": b_oof_rmse,
            "test_std": summarize_predictions(b_test_pred)["std"],
            "test_pred": b_test_pred,
        },
        {
            "model_name": "C_pls_plus_slope",
            "oof_rmse": c_oof_rmse,
            "test_std": summarize_predictions(c_test_pred)["std"],
            "test_pred": c_test_pred,
        },
    ]
    best = choose_best_model(results)
    best_name = str(best["model_name"])
    best_pred = np.asarray(best["test_pred"], dtype=np.float64)

    print("[Model selection]")
    print(f"selected_model={best_name}")
    print(f"selected_oof_rmse={float(best['oof_rmse']):.6f}")
    print(f"selected_test_std={float(best['test_std']):.6f}")
    print("")

    save_submission(test_df, best_pred)
    print(f"saved_submission={SUBMISSION_PATH}")


if __name__ == "__main__":
    main()
