"""
3-model ensemble: LocalPLS k=30 (clip) + LocalPLS k=200 + LightGBM
OOF-based weight search, clip(0) applied.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from scipy.signal import savgol_filter
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut

from _base_band2 import (
    load_data, select_band2, apply_snv,
    save_submission, SUBMISSIONS_DIR, EPS
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT_DIR = Path(__file__).resolve().parent
RESULTS_PATH = EXPERIMENT_DIR / "results.csv"

# ── configs ────────────────────────────────────────────────────────────────────
LGBM_PARAMS = {
    "n_estimators": 500, "learning_rate": 0.05, "num_leaves": 31,
    "min_child_samples": 20, "subsample": 0.8, "colsample_bytree": 0.8,
    "objective": "regression", "metric": "rmse",
    "verbose": -1, "random_state": 42, "n_jobs": -1,
}


# ── LocalPLS helpers ───────────────────────────────────────────────────────────

def apply_snv_sg1(X: np.ndarray) -> np.ndarray:
    mu = X.mean(axis=1, keepdims=True)
    sd = np.clip(X.std(axis=1, keepdims=True), EPS, None)
    X = (X - mu) / sd
    return savgol_filter(X, window_length=11, polyorder=2, deriv=1, axis=1)


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


def run_localpls_loso(X, y, groups, k, n_comp):
    logo = LeaveOneGroupOut()
    oof = np.zeros_like(y, dtype=np.float64)
    for fold, (tr, val) in enumerate(logo.split(X, y, groups), 1):
        oof[val] = predict_local_pls(X[tr], y[tr], X[val], k, n_comp)
        rmse = float(np.sqrt(mean_squared_error(y[val], oof[val])))
        print(f"  [LocalPLS k={k}] fold={fold} holdout={np.unique(groups[val]).tolist()} rmse={rmse:.4f}")
    return oof


# ── weight search ──────────────────────────────────────────────────────────────

def search_weights_3(oof_a, oof_b, oof_c, y, step=0.05):
    """Grid search w_a, w_b; w_c = 1 - w_a - w_b. Returns best (w_a, w_b, w_c, rmse)."""
    vals = np.arange(0.0, 1.0 + step / 2, step)
    best_rmse, best_w = float("inf"), (1/3, 1/3, 1/3)
    for wa in vals:
        for wb in vals:
            wc = 1.0 - wa - wb
            if wc < -1e-6:
                continue
            wc = max(0.0, wc)
            ens = wa * oof_a + wb * oof_b + wc * oof_c
            rmse = float(np.sqrt(mean_squared_error(y, np.clip(ens, 0, None))))
            if rmse < best_rmse:
                best_rmse, best_w = rmse, (wa, wb, wc)
    return best_w[0], best_w[1], best_w[2], best_rmse


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
    train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col = load_data()
    band2_cols = select_band2(wave_cols)

    X_raw = train_df[band2_cols].to_numpy(dtype=np.float64)
    y = train_df[target_col].to_numpy(dtype=np.float64)
    groups = train_df[species_col].to_numpy()
    X_test_raw = test_df[band2_cols].to_numpy(dtype=np.float64)
    sample_numbers = train_df[sample_col].to_numpy()

    print(f"band2_features={len(band2_cols)}")

    # ── A: LocalPLS k=30, snv_sg1 ─────────────────────────────────────────────
    print("\n[Model A] LocalPLS k=30 n=3 snv_sg1")
    Xp_sg1 = apply_snv_sg1(X_raw)
    oof_a = run_localpls_loso(Xp_sg1, y, groups, k=30, n_comp=3)
    rmse_a = float(np.sqrt(mean_squared_error(y, np.clip(oof_a, 0, None))))
    print(f"  LOSO clip RMSE = {rmse_a:.6f}")

    # ── B: LocalPLS k=200, snv_sg1 ────────────────────────────────────────────
    # Load from saved OOF if exists, else re-run
    oof_b_path = PROJECT_ROOT / "experiments" / "expLocalPLS_band2" / "oof_predictions.csv"
    if oof_b_path.exists():
        print(f"\n[Model B] LocalPLS k=200 n=3 snv_sg1 (loading saved OOF)")
        oof_b_df = pd.read_csv(oof_b_path)
        oof_b = oof_b_df["oof_pred"].to_numpy(dtype=np.float64)
    else:
        print("\n[Model B] LocalPLS k=200 n=3 snv_sg1 (re-running)")
        oof_b = run_localpls_loso(Xp_sg1, y, groups, k=200, n_comp=3)
    rmse_b = float(np.sqrt(mean_squared_error(y, np.clip(oof_b, 0, None))))
    print(f"  LOSO clip RMSE = {rmse_b:.6f}")

    # ── C: LightGBM snv ────────────────────────────────────────────────────────
    oof_c_path = PROJECT_ROOT / "experiments" / "expGBDT_band2" / "oof_predictions.csv"
    if oof_c_path.exists():
        print(f"\n[Model C] LightGBM snv (loading saved OOF)")
        oof_c_df = pd.read_csv(oof_c_path)
        oof_c = oof_c_df["oof_pred"].to_numpy(dtype=np.float64)
    else:
        print("\n[Model C] LightGBM snv (re-running)")
        logo = LeaveOneGroupOut()
        X_snv = apply_snv(X_raw)
        oof_c = np.zeros_like(y, dtype=np.float64)
        for fold, (tr, val) in enumerate(logo.split(X_snv, y, groups), 1):
            m = LGBMRegressor(**LGBM_PARAMS)
            m.fit(X_snv[tr], y[tr])
            oof_c[val] = m.predict(X_snv[val])
            print(f"  [LGBM] fold={fold} rmse={np.sqrt(mean_squared_error(y[val], oof_c[val])):.4f}")
    rmse_c = float(np.sqrt(mean_squared_error(y, np.clip(oof_c, 0, None))))
    print(f"  LOSO clip RMSE = {rmse_c:.6f}")

    # Save LocalPLS k=30 OOF
    oof_a_path = PROJECT_ROOT / "experiments" / "expLocalPLS_band2" / "oof_k30_predictions.csv"
    pd.DataFrame({"sample_number": sample_numbers, "oof_pred": oof_a, "true_mc": y}).to_csv(
        oof_a_path, index=False, encoding="utf-8"
    )
    print(f"\nsaved oof_k30 → {oof_a_path}")

    # ── Weight search ──────────────────────────────────────────────────────────
    print("\n[Weight search] step=0.05 ...")
    wa, wb, wc, best_rmse = search_weights_3(oof_a, oof_b, oof_c, y, step=0.05)
    print(f"  best: w_k30={wa:.2f}  w_k200={wb:.2f}  w_lgbm={wc:.2f}  loso_clip={best_rmse:.6f}")

    # Fine search around best
    print("[Fine search] step=0.01 ...")
    fine_vals = np.arange(max(0, wa - 0.1), min(1.0, wa + 0.11), 0.01)
    for wa2 in fine_vals:
        for wb2 in np.arange(max(0, wb - 0.1), min(1.0, wb + 0.11), 0.01):
            wc2 = 1.0 - wa2 - wb2
            if wc2 < -1e-6: continue
            wc2 = max(0.0, wc2)
            ens = wa2 * oof_a + wb2 * oof_b + wc2 * oof_c
            rmse = float(np.sqrt(mean_squared_error(y, np.clip(ens, 0, None))))
            if rmse < best_rmse:
                best_rmse, wa, wb, wc = rmse, wa2, wb2, wc2
    print(f"  fine best: w_k30={wa:.3f}  w_k200={wb:.3f}  w_lgbm={wc:.3f}  loso_clip={best_rmse:.6f}")

    # Results table (coarse grid)
    rows = []
    for wa2 in np.arange(0.0, 1.01, 0.1):
        for wb2 in np.arange(0.0, 1.01 - wa2, 0.1):
            wc2 = max(0.0, round(1.0 - wa2 - wb2, 6))
            ens = wa2 * oof_a + wb2 * oof_b + wc2 * oof_c
            rmse = float(np.sqrt(mean_squared_error(y, np.clip(ens, 0, None))))
            rows.append({"w_k30": round(wa2, 2), "w_k200": round(wb2, 2), "w_lgbm": round(wc2, 2), "ensemble_loso_rmse": rmse})
    results_df = pd.DataFrame(rows).sort_values("ensemble_loso_rmse").reset_index(drop=True)
    results_df["localpls_k30_loso_clip"] = rmse_a
    results_df["localpls_k200_loso_clip"] = rmse_b
    results_df["lgbm_loso_clip"] = rmse_c
    results_df.to_csv(RESULTS_PATH, index=False, encoding="utf-8")
    print(f"\nTop 10 weight combinations:")
    print(results_df.head(10)[["w_k30","w_k200","w_lgbm","ensemble_loso_rmse"]].to_string(index=False))
    print(f"saved_results={RESULTS_PATH}")

    # ── Test predictions ───────────────────────────────────────────────────────
    print("\n[Test predictions]")
    Xp_sg1_test = apply_snv_sg1(X_test_raw)
    test_a = predict_local_pls(Xp_sg1, y, Xp_sg1_test, k=30, n_comp=3)
    test_b = predict_local_pls(Xp_sg1, y, Xp_sg1_test, k=200, n_comp=3)

    X_snv_all = apply_snv(X_raw); X_snv_test = apply_snv(X_test_raw)
    lgbm_full = LGBMRegressor(**LGBM_PARAMS)
    lgbm_full.fit(X_snv_all, y)
    test_c = lgbm_full.predict(X_snv_test)

    test_ens = np.clip(wa * test_a + wb * test_b + wc * test_c, 0, None)
    print(f"  test_min={test_ens.min():.4f}  test_max={test_ens.max():.4f}")

    submission_path = SUBMISSIONS_DIR / f"expA046_ensemble3_k30w{wa:.2f}_k200w{wb:.2f}_lgbmw{wc:.2f}_submission.csv"
    save_submission(sample_submit_df, test_df, sample_col, test_ens, submission_path)
    print(f"saved_submission={submission_path.name}")
    print(f"\nbest_ensemble_loso_clip={best_rmse:.6f}")


if __name__ == "__main__":
    main()
