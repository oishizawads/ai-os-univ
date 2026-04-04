"""
Sub-band statistics as LocalPLS representation.
band2 を3サブバンドに分割し、各サブバンドの統計量（mean/slope/area）を特徴量として
LocalPLSの近傍探索に使用する。
Sub-bands (cm-1):
  Sub1: 4800-5000  free water OH combination
  Sub2: 5000-5200  free water OH overtone
  Sub3: 5200-5350  bound water OH combination
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut
from _base_band2 import (
    load_data, select_band2, apply_snv, apply_snv_sg1,
    save_submission, SUBMISSIONS_DIR, EPS
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

EXPERIMENT_DIR = Path(__file__).resolve().parent
RESULTS_PATH = EXPERIMENT_DIR / "results.csv"

SUB_BANDS = [(4800.0, 5000.0), (5000.0, 5200.0), (5200.0, 5350.0)]
FULL_BAND2 = (4800.0, 5350.0)

K_VALUES = [20, 30, 50, 100]
N_COMP_VALUES = [3, 5]


def get_band_indices(wave_cols, lo, hi):
    wn = np.array([float(c) for c in wave_cols])
    return np.where((wn >= lo) & (wn <= hi))[0]


def sub_band_features(X: np.ndarray, wave_cols: list[str], preproc: str) -> np.ndarray:
    """
    For each sub-band compute: mean, linear slope, area (trapz).
    Returns shape (n_samples, 9) = 3 sub-bands × 3 stats.
    """
    # Apply preprocessing on full band2 first
    if preproc == "snv":
        Xp = apply_snv(X)
    elif preproc == "snv_sg1":
        Xp = apply_snv_sg1(X)
    else:
        Xp = X.copy()

    wn = np.array([float(c) for c in wave_cols])
    feats = []
    for lo, hi in SUB_BANDS:
        idx = np.where((wn >= lo) & (wn <= hi))[0]
        Xs = Xp[:, idx]
        wns = wn[idx]

        # mean
        mean_val = Xs.mean(axis=1)

        # linear slope (polyfit degree 1 coefficient)
        wn_norm = (wns - wns.mean()) / (wns.std() + EPS)
        # least squares: slope = (Xs @ wn_norm) / (wn_norm @ wn_norm)
        slope_val = (Xs @ wn_norm) / (wn_norm @ wn_norm + EPS)

        # area (trapz approximation)
        dw = np.diff(wns)
        area_val = ((Xs[:, :-1] + Xs[:, 1:]) / 2.0 @ dw)

        feats.extend([mean_val, slope_val, area_val])

    return np.column_stack(feats)  # (n_samples, 9)


def normalize_rows(X: np.ndarray) -> np.ndarray:
    return X / np.clip(np.linalg.norm(X, axis=1, keepdims=True), 1e-12, None)


def predict_local_pls(X_train, y_train, X_query, k, n_comp):
    k_eff = min(k, len(X_train))
    sims = normalize_rows(X_query) @ normalize_rows(X_train).T
    topk = np.argpartition(-sims, kth=k_eff - 1, axis=1)[:, :k_eff]
    preds = []
    for i, idx in enumerate(topk):
        idx = idx[np.argsort(-sims[i, idx])]
        Xl, yl = X_train[idx], y_train[idx]
        mc = min(n_comp, Xl.shape[0] - 1, Xl.shape[1])
        if mc < 1:
            preds.append(float(np.mean(yl)))
            continue
        m = PLSRegression(n_components=mc, max_iter=500)
        m.fit(Xl, yl)
        preds.append(float(m.predict(X_query[i:i+1]).ravel()[0]))
    return np.array(preds, dtype=np.float64)


SETTINGS = [
    ("snv_subband",     "snv"),
    ("snv_sg1_subband", "snv_sg1"),
]


def main():
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
    train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col = load_data()
    band2_cols = select_band2(wave_cols)
    X = train_df[band2_cols].to_numpy(dtype=np.float64)
    y = train_df[target_col].to_numpy(dtype=np.float64)
    groups = train_df[species_col].to_numpy()
    X_test = test_df[band2_cols].to_numpy(dtype=np.float64)
    logo = LeaveOneGroupOut()
    print(f"band2_features={len(band2_cols)}")
    print(f"sub_bands={SUB_BANDS}")

    results = []
    best_rmse, best_cfg = float("inf"), None
    total = len(SETTINGS) * len(K_VALUES) * len(N_COMP_VALUES)
    done = 0

    for preproc_name, preproc in SETTINGS:
        # Build sub-band feature representations
        X_feat = sub_band_features(X, band2_cols, preproc)
        X_test_feat = sub_band_features(X_test, band2_cols, preproc)
        # Also keep original band2 preprocessed for PLS regression within neighbors
        if preproc == "snv":
            X_orig = apply_snv(X)
            X_test_orig = apply_snv(X_test)
        else:
            X_orig = apply_snv_sg1(X)
            X_test_orig = apply_snv_sg1(X_test)

        print(f"\n[{preproc_name}] sub-band feature shape={X_feat.shape}")

        for k in K_VALUES:
            for n_comp in N_COMP_VALUES:
                oof = np.zeros_like(y, dtype=np.float64)
                for tr, val in logo.split(X_feat, y, groups):
                    # Use sub-band features for neighbor finding
                    # Use original band2 features for local PLS regression
                    preds = predict_local_pls(
                        X_train=X_feat[tr],   # neighbor search space
                        y_train=y[tr],
                        X_query=X_feat[val],
                        k=k, n_comp=n_comp
                    )
                    oof[val] = preds

                rmse = float(np.sqrt(mean_squared_error(y, oof)))
                results.append({"setting": preproc_name, "k": k, "n_comp": n_comp, "loso_rmse": rmse})
                done += 1
                print(f"  [{done}/{total}] k={k} n_comp={n_comp} loso={rmse:.6f}")
                if rmse < best_rmse:
                    best_rmse = rmse
                    best_cfg = (preproc_name, preproc, k, n_comp, X_feat, X_test_feat)

    results_df = pd.DataFrame(results).sort_values("loso_rmse").reset_index(drop=True)
    results_df.to_csv(RESULTS_PATH, index=False, encoding="utf-8")
    print("\nTop 10:")
    print(results_df.head(10).to_string(index=False))
    print(f"\nsaved_results={RESULTS_PATH}")

    # Test predictions
    name, preproc, k, n_comp, X_feat_all, X_test_feat_all = best_cfg
    preds = predict_local_pls(X_feat_all, y, X_test_feat_all, k=k, n_comp=n_comp)
    print(f"\nbest={name} k={k} n_comp={n_comp} loso={best_rmse:.6f}")
    print(f"pred_min={preds.min():.4f} pred_max={preds.max():.4f}")
    preds = np.clip(preds, 0, None)
    save_submission(sample_submit_df, test_df, sample_col, preds,
                    SUBMISSIONS_DIR / f"expA048_subband_localpls_{name}_k{k}_n{n_comp}_submission.csv")
    print(f"saved_submission=expA048_subband_localpls_{name}_k{k}_n{n_comp}_submission.csv")


if __name__ == "__main__":
    main()
