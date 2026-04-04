from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut


DATA_PATH = Path("C:/workspace/ai-os/competitions/near-infrared-challenge/data/raw/train.csv")
OUTPUT_DIR = Path("C:/workspace/ai-os/competitions/near-infrared-challenge/experiments/expPinpoint")
EPS = 1e-6
TOP_N_LIST = [5, 10, 20, 30, 50, 80, 100, 300, 500]
BAND2_RANGE = (4800.0, 5350.0)


def snv(x: np.ndarray) -> np.ndarray:
    row_mean = x.mean(axis=1, keepdims=True)
    row_std = x.std(axis=1, keepdims=True)
    row_std = np.where(row_std < 1e-10, 1e-10, row_std)
    return (x - row_mean) / row_std


def load_data() -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    df = pd.read_csv(DATA_PATH, encoding="cp932")
    spectral_cols = df.columns[4:].tolist()
    wavenumbers = np.array([float(col) for col in spectral_cols], dtype=np.float64)
    x_raw = df.iloc[:, 4:].to_numpy(dtype=np.float64)
    y = df.iloc[:, 3].to_numpy(dtype=np.float64)
    groups = df.iloc[:, 1].to_numpy()
    return df, wavenumbers, x_raw, y, groups


def compute_abs_corr(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    x_centered = x - x.mean(axis=0, keepdims=True)
    y_centered = y - y.mean()
    numerator = np.abs((x_centered * y_centered[:, None]).sum(axis=0))
    denominator = np.sqrt((x_centered**2).sum(axis=0) * (y_centered**2).sum())
    return numerator / np.maximum(denominator, 1e-12)


def compute_species_f(x: np.ndarray, groups: np.ndarray) -> np.ndarray:
    unique_groups = np.unique(groups)
    n_samples, n_features = x.shape
    n_groups = len(unique_groups)
    overall_mean = x.mean(axis=0)

    ss_between = np.zeros(n_features, dtype=np.float64)
    ss_within = np.zeros(n_features, dtype=np.float64)

    for group in unique_groups:
        mask = groups == group
        x_group = x[mask]
        group_size = x_group.shape[0]
        group_mean = x_group.mean(axis=0)
        ss_between += group_size * (group_mean - overall_mean) ** 2
        ss_within += ((x_group - group_mean) ** 2).sum(axis=0)

    df_between = max(n_groups - 1, 1)
    df_within = max(n_samples - n_groups, 1)
    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    return ms_between / np.maximum(ms_within, 1e-12)


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def loso_pls(
    x_raw_subset: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    n_components: int,
) -> tuple[float, float, float, np.ndarray]:
    logo = LeaveOneGroupOut()
    oof_pred = np.zeros(len(y), dtype=np.float64)
    fold_rmses: list[float] = []

    for train_idx, valid_idx in logo.split(x_raw_subset, y, groups):
        x_train = snv(x_raw_subset[train_idx])
        x_valid = snv(x_raw_subset[valid_idx])
        max_components = min(n_components, x_train.shape[0] - 1, x_train.shape[1])

        if max_components < 1:
            pred = np.full(len(valid_idx), y[train_idx].mean(), dtype=np.float64)
        else:
            model = PLSRegression(n_components=max_components, max_iter=500)
            model.fit(x_train, y[train_idx])
            pred = model.predict(x_valid).ravel()

        oof_pred[valid_idx] = pred
        fold_rmses.append(rmse(y[valid_idx], pred))

    return rmse(y, oof_pred), float(np.mean(fold_rmses)), float(np.std(fold_rmses)), oof_pred


def summarize_wavenumbers(wavenumbers: np.ndarray) -> str:
    if len(wavenumbers) == 0:
        return "NA"
    sorted_wn = np.sort(wavenumbers)
    return f"{sorted_wn[0]:.2f}-{sorted_wn[-1]:.2f} cm-1"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    train_df, wavenumbers, x_raw, y, groups = load_data()
    x_snv_full = snv(x_raw)
    band2_mask = (wavenumbers >= BAND2_RANGE[0]) & (wavenumbers <= BAND2_RANGE[1])
    band2_indices = np.flatnonzero(band2_mask)

    moisture_corr = compute_abs_corr(x_snv_full, y)
    species_f = compute_species_f(x_snv_full, groups)
    signal_ratio = moisture_corr / (species_f + EPS)

    feature_df = pd.DataFrame(
        {
            "feature_index": np.arange(len(wavenumbers), dtype=int),
            "wavenumber": wavenumbers,
            "moisture_corr": moisture_corr,
            "species_F": species_f,
            "signal_ratio": signal_ratio,
            "is_band2": band2_mask,
        }
    ).sort_values("signal_ratio", ascending=False, ignore_index=True)
    feature_df.to_csv(OUTPUT_DIR / "signal_ratio_all_wavelengths.csv", index=False)

    top30_df = feature_df.head(30).copy()
    top30_df.to_csv(OUTPUT_DIR / "signal_ratio_top30.csv", index=False)

    ranked_indices = feature_df["feature_index"].to_numpy(dtype=int)
    eval_rows: list[dict[str, float | int | str]] = []

    for n in TOP_N_LIST:
        selected = ranked_indices[:n]
        n_components = min(n // 5, 15)
        score, fold_mean, fold_std, _ = loso_pls(x_raw[:, selected], y, groups, n_components)
        eval_rows.append(
            {
                "selection": f"global_top{n}",
                "n_wavelengths": n,
                "n_components": n_components,
                "loso_oof_rmse": score,
                "fold_mean": fold_mean,
                "fold_std": fold_std,
                "wavenumber_range": summarize_wavenumbers(wavenumbers[selected]),
            }
        )

    band2_full_components = min(band2_mask.sum() // 5, 15)
    band2_full_score, band2_full_mean, band2_full_std, _ = loso_pls(
        x_raw[:, band2_mask], y, groups, band2_full_components
    )
    eval_rows.append(
        {
            "selection": "band2_full",
            "n_wavelengths": int(band2_mask.sum()),
            "n_components": band2_full_components,
            "loso_oof_rmse": band2_full_score,
            "fold_mean": band2_full_mean,
            "fold_std": band2_full_std,
            "wavenumber_range": summarize_wavenumbers(wavenumbers[band2_mask]),
        }
    )

    eval_df = pd.DataFrame(eval_rows).sort_values("loso_oof_rmse", ignore_index=True)
    eval_df.to_csv(OUTPUT_DIR / "loso_pls_by_topn.csv", index=False)

    band2_ranked = feature_df[feature_df["is_band2"]].copy().reset_index(drop=True)
    band2_top20 = band2_ranked.head(20).copy()
    band2_top20.to_csv(OUTPUT_DIR / "band2_signal_ratio_top20.csv", index=False)

    band2_top20_indices = band2_top20["feature_index"].to_numpy(dtype=int)
    band2_top20_components = min(len(band2_top20_indices) // 5, 15)
    band2_top20_score, band2_top20_mean, band2_top20_std, _ = loso_pls(
        x_raw[:, band2_top20_indices], y, groups, band2_top20_components
    )

    band2_baseline_n10_score, band2_baseline_n10_mean, band2_baseline_n10_std, _ = loso_pls(
        x_raw[:, band2_mask], y, groups, 10
    )

    band2_compare_df = pd.DataFrame(
        [
            {
                "selection": "band2_top20_signal_ratio",
                "n_wavelengths": 20,
                "n_components": band2_top20_components,
                "loso_oof_rmse": band2_top20_score,
                "fold_mean": band2_top20_mean,
                "fold_std": band2_top20_std,
                "wavenumber_range": summarize_wavenumbers(wavenumbers[band2_top20_indices]),
            },
            {
                "selection": "band2_full_rule_based",
                "n_wavelengths": int(band2_mask.sum()),
                "n_components": band2_full_components,
                "loso_oof_rmse": band2_full_score,
                "fold_mean": band2_full_mean,
                "fold_std": band2_full_std,
                "wavenumber_range": summarize_wavenumbers(wavenumbers[band2_mask]),
            },
            {
                "selection": "band2_full_baseline_n10",
                "n_wavelengths": int(band2_mask.sum()),
                "n_components": 10,
                "loso_oof_rmse": band2_baseline_n10_score,
                "fold_mean": band2_baseline_n10_mean,
                "fold_std": band2_baseline_n10_std,
                "wavenumber_range": summarize_wavenumbers(wavenumbers[band2_mask]),
            },
        ]
    ).sort_values("loso_oof_rmse", ignore_index=True)
    band2_compare_df.to_csv(OUTPUT_DIR / "band2_top20_vs_full.csv", index=False)

    best_row = eval_df.iloc[0]
    best_band2_compare_row = band2_compare_df.iloc[0]

    print("=== Signal Ratio Top30 ===")
    print(
        top30_df[["wavenumber", "moisture_corr", "species_F", "signal_ratio"]]
        .to_string(index=False, float_format=lambda v: f"{v:.6f}")
    )
    print("")

    print("=== LOSO RMSE by Selection ===")
    print(
        eval_df[
            [
                "selection",
                "n_wavelengths",
                "n_components",
                "loso_oof_rmse",
                "fold_mean",
                "fold_std",
                "wavenumber_range",
            ]
        ].to_string(index=False, float_format=lambda v: f"{v:.6f}" if isinstance(v, float) else str(v))
    )
    print("")

    print("=== band2 Top20 vs band2 Full ===")
    print(
        band2_compare_df[
            [
                "selection",
                "n_wavelengths",
                "n_components",
                "loso_oof_rmse",
                "fold_mean",
                "fold_std",
                "wavenumber_range",
            ]
        ].to_string(index=False, float_format=lambda v: f"{v:.6f}" if isinstance(v, float) else str(v))
    )
    print("")

    print("=== Conclusion ===")
    print(
        f"best_requested_sweep={best_row['selection']} "
        f"n_wavelengths={int(best_row['n_wavelengths'])} "
        f"n_components={int(best_row['n_components'])} "
        f"loso_oof_rmse={best_row['loso_oof_rmse']:.6f} "
        f"range={best_row['wavenumber_range']}"
    )
    print(
        f"best_band2_comparison={best_band2_compare_row['selection']} "
        f"n_wavelengths={int(best_band2_compare_row['n_wavelengths'])} "
        f"n_components={int(best_band2_compare_row['n_components'])} "
        f"loso_oof_rmse={best_band2_compare_row['loso_oof_rmse']:.6f} "
        f"range={best_band2_compare_row['wavenumber_range']}"
    )
    print(
        f"saved_signal_ratio={OUTPUT_DIR / 'signal_ratio_all_wavelengths.csv'}\n"
        f"saved_eval={OUTPUT_DIR / 'loso_pls_by_topn.csv'}\n"
        f"saved_band2_compare={OUTPUT_DIR / 'band2_top20_vs_full.csv'}"
    )


if __name__ == "__main__":
    main()
