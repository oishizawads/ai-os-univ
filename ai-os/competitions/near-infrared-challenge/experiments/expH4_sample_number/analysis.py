from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TRAIN_PATH = PROJECT_ROOT / "data" / "raw" / "train.csv"
TEST_PATH = PROJECT_ROOT / "data" / "raw" / "test.csv"
ENCODING = "cp932"

ID_COL = "sample number"
SPECIES_COL = "species number"
SPECIES_NAME_COL = "樹種"
TARGET_COL = "含水率"


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    train_df = pd.read_csv(TRAIN_PATH, encoding=ENCODING)
    test_df = pd.read_csv(TEST_PATH, encoding=ENCODING)
    wave_cols = train_df.columns[4:].tolist()
    return train_df, test_df, wave_cols


def print_series_edges(name: str, values: pd.Series) -> None:
    sorted_values = values.sort_values().reset_index(drop=True)
    print(f"[{name}] sample number sorted first 20")
    print(sorted_values.head(20).to_list())
    print(f"[{name}] sample number sorted last 20")
    print(sorted_values.tail(20).to_list())
    print("")


def analyze_interleave(train_ids: pd.Series, test_ids: pd.Series) -> None:
    merged = pd.concat(
        [
            pd.DataFrame({ID_COL: train_ids.to_numpy(), "source": "train"}),
            pd.DataFrame({ID_COL: test_ids.to_numpy(), "source": "test"}),
        ],
        ignore_index=True,
    ).sort_values(ID_COL, kind="mergesort").reset_index(drop=True)

    sources = merged["source"].to_numpy()
    switch_flags = sources[1:] != sources[:-1]
    switch_rate = float(switch_flags.mean())
    same_source_pairs = int((~switch_flags).sum())

    starts_with = str(sources[0])
    perfect_alternation = bool(np.all(switch_flags))
    odd_positions = merged.iloc[::2]["source"].value_counts().to_dict()
    even_positions = merged.iloc[1::2]["source"].value_counts().to_dict()

    print("[Interleave check]")
    print(f"train_count={len(train_ids)} test_count={len(test_ids)} total={len(merged)}")
    print(f"starts_with={starts_with}")
    print(f"adjacent_switch_rate={switch_rate:.6f}")
    print(f"same_source_adjacent_pairs={same_source_pairs}")
    print(f"perfect_alternation={perfect_alternation}")
    print(f"odd_positions_source_counts={odd_positions}")
    print(f"even_positions_source_counts={even_positions}")
    print("first_40_sorted_with_source:")
    print(merged.head(40).to_string(index=False))
    print("")


def corr_or_nan(x: pd.Series, y: pd.Series) -> float:
    if x.nunique() <= 1 or y.nunique() <= 1:
        return float("nan")
    return float(x.corr(y))


def print_correlations(train_df: pd.DataFrame) -> None:
    print("[Correlation: sample_number vs moisture]")
    overall_corr = corr_or_nan(train_df[ID_COL], train_df[TARGET_COL])
    print(f"overall_corr={overall_corr:.6f}")
    print("by_species:")

    rows = []
    for species, part in train_df.groupby(SPECIES_COL, sort=True):
        rows.append(
            {
                "species_number": int(species),
                "n": int(len(part)),
                "corr": corr_or_nan(part[ID_COL], part[TARGET_COL]),
                "sample_min": int(part[ID_COL].min()),
                "sample_max": int(part[ID_COL].max()),
            }
        )

    corr_df = pd.DataFrame(rows)
    print(corr_df.to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print("")


def evaluate_models(train_df: pd.DataFrame, wave_cols: list[str]) -> None:
    x_raw = train_df[wave_cols].to_numpy(dtype=np.float64)
    x_id = train_df[[ID_COL]].to_numpy(dtype=np.float64)
    x_raw_plus_id = np.hstack([x_raw, x_id])
    y = train_df[TARGET_COL].to_numpy(dtype=np.float64)
    groups = train_df[SPECIES_COL].to_numpy()

    models = {
        "PLS_raw_n15": PLSRegression(n_components=15, max_iter=500),
        "Ridge_sample_number_only": Pipeline(
            [
                ("scaler", StandardScaler()),
                ("ridge", Ridge(alpha=1.0)),
            ]
        ),
        "PLS_raw_plus_sample_number_n15": PLSRegression(n_components=15, max_iter=500),
    }
    features = {
        "PLS_raw_n15": x_raw,
        "Ridge_sample_number_only": x_id,
        "PLS_raw_plus_sample_number_n15": x_raw_plus_id,
    }

    splitter = GroupKFold(n_splits=5)
    print("[GroupKFold(5) OOF RMSE by species]")
    rows = []
    for name, model in models.items():
        x = features[name]
        oof = np.zeros(len(train_df), dtype=np.float64)
        fold_scores: list[float] = []
        for fold, (tr_idx, va_idx) in enumerate(splitter.split(x, y, groups), start=1):
            model.fit(x[tr_idx], y[tr_idx])
            pred = model.predict(x[va_idx]).ravel()
            oof[va_idx] = pred
            fold_scores.append(rmse(y[va_idx], pred))

        rows.append(
            {
                "model": name,
                "oof_rmse": rmse(y, oof),
                "fold_rmse_mean": float(np.mean(fold_scores)),
                "fold_rmse_std": float(np.std(fold_scores)),
            }
        )

    result_df = pd.DataFrame(rows).sort_values("oof_rmse").reset_index(drop=True)
    print(result_df.to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    print("")


def print_test_pred_distribution(train_df: pd.DataFrame, test_df: pd.DataFrame) -> None:
    x_train = train_df[[ID_COL]].to_numpy(dtype=np.float64)
    y_train = train_df[TARGET_COL].to_numpy(dtype=np.float64)
    x_test = test_df[[ID_COL]].to_numpy(dtype=np.float64)

    model = LinearRegression()
    model.fit(x_train, y_train)
    pred = model.predict(x_test)

    print("[LinearRegression(sample_number -> moisture) on test]")
    print(f"coef={float(model.coef_[0]):.6f}")
    print(f"intercept={float(model.intercept_):.6f}")
    print(f"mean={float(pred.mean()):.6f}")
    print(f"std={float(pred.std()):.6f}")
    print(f"min={float(pred.min()):.6f}")
    print(f"max={float(pred.max()):.6f}")
    print("")


def main() -> None:
    train_df, test_df, wave_cols = load_data()

    print(f"train_shape={train_df.shape}")
    print(f"test_shape={test_df.shape}")
    print(f"n_wave_cols={len(wave_cols)}")
    print("")

    print_series_edges("train", train_df[ID_COL])
    print_series_edges("test", test_df[ID_COL])
    analyze_interleave(train_df[ID_COL], test_df[ID_COL])
    print_correlations(train_df)
    evaluate_models(train_df, wave_cols)
    print_test_pred_distribution(train_df, test_df)


if __name__ == "__main__":
    main()
