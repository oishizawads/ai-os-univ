"""
expA055_kfold_calibration
KFold(5, shuffle=True, seed=42) で既知LBモデルを再評価。
KFold vs LOSO vs public LB の乖離を比較する。

既知LB:
  Ridge raw:               KFold OOF=18.62  → LB=21.5
  PLS KFold:               KFold OOF=13.12  → LB=31.83
  LocalPLS k=30 snv_sg1:   LOSO=18.04       → LB=26.30
  4-model ensemble:        LOSO=16.42       → LB=26.11
"""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold, LeaveOneGroupOut
from sklearn.cross_decomposition import PLSRegression
from scipy.signal import savgol_filter

from _base_band2 import (
    load_data, select_band2, apply_snv, apply_snv_sg1, EPS,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

EXPERIMENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT   = Path(__file__).resolve().parents[2]
A053_PARAMS    = PROJECT_ROOT / "experiments" / "expA053_optuna_all" / "best_params"

SEED    = 42
N_FOLDS = 5
KF      = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)

KNOWN_LB = {
    "ridge_raw_kfold":          21.5,
    "pls_raw_kfold":            31.83,
    "localpls_k30_snv_sg1_loso": 26.30,
    "ensemble4_loso":           26.11,
}
KNOWN_CV = {
    "ridge_raw_kfold":          ("kfold", 18.62),
    "pls_raw_kfold":            ("kfold", 13.12),
    "localpls_k30_snv_sg1_loso": ("loso",  18.04),
    "ensemble4_loso":           ("loso",  16.42),
}


# ---------------------------------------------------------------------------
# LocalPLS helpers
# ---------------------------------------------------------------------------

def _normalize(X):
    return X / np.clip(np.linalg.norm(X, axis=1, keepdims=True), 1e-12, None)


def predict_local_pls(X_train, y_train, X_query, k, n_comp):
    k_eff = min(k, len(X_train))
    sims  = _normalize(X_query) @ _normalize(X_train).T
    topk  = np.argpartition(-sims, kth=k_eff - 1, axis=1)[:, :k_eff]
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


def kfold_rmse(predict_fn, X, y):
    """predict_fn(X_tr, y_tr, X_val) -> oof_val"""
    oof = np.zeros_like(y, dtype=np.float64)
    for fold, (tr, val) in enumerate(KF.split(X), 1):
        oof[val] = predict_fn(X[tr], y[tr], X[val])
        rmse = float(np.sqrt(mean_squared_error(y[val], oof[val])))
        print(f"    fold={fold}  rmse={rmse:.4f}")
    return float(np.sqrt(mean_squared_error(y, np.clip(oof, 0, None)))), oof


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)

    train_df, test_df, _, wave_cols, sample_col, species_col, target_col = load_data()
    band2_cols = select_band2(wave_cols)
    X_raw  = train_df[band2_cols].to_numpy(dtype=np.float64)
    X_full = train_df[wave_cols].to_numpy(dtype=np.float64)   # full spectrum for Ridge
    y      = train_df[target_col].to_numpy(dtype=np.float64)
    groups = train_df[species_col].to_numpy()

    X_snv  = apply_snv(X_raw)
    X_sg1  = apply_snv_sg1(X_raw)

    results = []

    # ── 1. Ridge raw full spectrum (KFold baseline, already known) ─────────
    print("\n[1] Ridge raw full spectrum  (KFold — already known: 18.62)")
    from sklearn.linear_model import Ridge
    def pred_ridge_raw(Xtr, ytr, Xval):
        m = Ridge(alpha=1.0); m.fit(Xtr, ytr); return m.predict(Xval)
    rmse1, _ = kfold_rmse(pred_ridge_raw, X_full, y)
    print(f"  KFold RMSE = {rmse1:.4f}  (reference: 18.62)  LB=21.5")
    results.append({"model": "ridge_raw_kfold", "kfold_rmse": rmse1,
                    "known_cv": 18.62, "known_cv_type": "kfold", "public_lb": 21.5})

    # ── 2. PLS raw full spectrum (KFold, already known) ────────────────────
    print("\n[2] PLS(n=25) raw full spectrum  (KFold — already known: 13.12)")
    def pred_pls_raw(Xtr, ytr, Xval):
        m = PLSRegression(n_components=25, max_iter=500)
        m.fit(Xtr, ytr); return m.predict(Xval).ravel()
    rmse2, _ = kfold_rmse(pred_pls_raw, X_full, y)
    print(f"  KFold RMSE = {rmse2:.4f}  (reference: 13.12)  LB=31.83")
    results.append({"model": "pls_raw_kfold", "kfold_rmse": rmse2,
                    "known_cv": 13.12, "known_cv_type": "kfold", "public_lb": 31.83})

    # ── 3. LocalPLS k=30 band2 snv_sg1 (LOSO=18.04 → LB=26.30) ───────────
    print("\n[3] LocalPLS k=30 band2 snv_sg1  (LOSO=18.04 → LB=26.30)")
    def pred_localpls_k30(Xtr, ytr, Xval):
        return predict_local_pls(Xtr, ytr, Xval, k=30, n_comp=3)
    rmse3, oof3 = kfold_rmse(pred_localpls_k30, X_sg1, y)
    print(f"  KFold RMSE = {rmse3:.4f}  LOSO=18.04  LB=26.30")
    results.append({"model": "localpls_k30_snv_sg1", "kfold_rmse": rmse3,
                    "known_cv": 18.04, "known_cv_type": "loso", "public_lb": 26.30})

    # ── 4. LGBM Optuna band2 snv ───────────────────────────────────────────
    print("\n[4] LGBM Optuna band2 snv")
    from lightgbm import LGBMRegressor
    lgbm_p = json.loads((A053_PARAMS / "lgbm_snv.json").read_text())
    lgbm_params = dict(objective="regression", metric="rmse", verbose=-1,
                       n_jobs=-1, random_state=SEED, subsample_freq=1, **lgbm_p)
    def pred_lgbm(Xtr, ytr, Xval):
        m = LGBMRegressor(**lgbm_params); m.fit(Xtr, ytr); return m.predict(Xval)
    rmse4, oof4 = kfold_rmse(pred_lgbm, X_snv, y)
    print(f"  KFold RMSE = {rmse4:.4f}  LOSO=17.61")
    results.append({"model": "lgbm_snv_optuna", "kfold_rmse": rmse4,
                    "known_cv": 17.61, "known_cv_type": "loso", "public_lb": None})

    # ── 5. XGB Optuna band2 snv ────────────────────────────────────────────
    print("\n[5] XGB Optuna band2 snv")
    from xgboost import XGBRegressor
    xgb_p = json.loads((A053_PARAMS / "xgb_snv.json").read_text())
    xgb_params = dict(objective="reg:squarederror", verbosity=0,
                      random_state=SEED, n_jobs=-1, tree_method="hist", **xgb_p)
    def pred_xgb(Xtr, ytr, Xval):
        m = XGBRegressor(**xgb_params); m.fit(Xtr, ytr); return m.predict(Xval)
    rmse5, oof5 = kfold_rmse(pred_xgb, X_snv, y)
    print(f"  KFold RMSE = {rmse5:.4f}  LOSO=17.55")
    results.append({"model": "xgb_snv_optuna", "kfold_rmse": rmse5,
                    "known_cv": 17.55, "known_cv_type": "loso", "public_lb": None})

    # ── 6. 4-model ensemble (KFold OOF weights from expA054) ───────────────
    # Use weights from expA054: k30=0.37, k200=0.20, lgbm=0.17, xgb=0.26
    # But compute k200 KFold OOF too
    print("\n[6] LocalPLS k=200 band2 snv_sg1")
    def pred_localpls_k200(Xtr, ytr, Xval):
        return predict_local_pls(Xtr, ytr, Xval, k=200, n_comp=3)
    rmse6, oof6 = kfold_rmse(pred_localpls_k200, X_sg1, y)
    print(f"  KFold RMSE = {rmse6:.4f}  LOSO=18.08")
    results.append({"model": "localpls_k200_snv_sg1", "kfold_rmse": rmse6,
                    "known_cv": 18.08, "known_cv_type": "loso", "public_lb": None})

    print("\n[7] 4-model ensemble (LOSO weights: k30=0.37, k200=0.20, lgbm=0.17, xgb=0.26)")
    w_k30, w_k200, w_lgbm, w_xgb = 0.37, 0.20, 0.17, 0.26
    oof_ens = w_k30 * oof3 + w_k200 * oof6 + w_lgbm * oof4 + w_xgb * oof5
    rmse_ens = float(np.sqrt(mean_squared_error(y, np.clip(oof_ens, 0, None))))
    print(f"  KFold RMSE (LOSO weights) = {rmse_ens:.4f}  LOSO=16.42  LB=26.11")
    results.append({"model": "ensemble4_loso_weights", "kfold_rmse": rmse_ens,
                    "known_cv": 16.42, "known_cv_type": "loso", "public_lb": 26.11})

    # Re-search weights on KFold OOF
    print("\n  Re-searching weights on KFold OOF ...")
    oofs = [oof3, oof6, oof4, oof5]
    best_rmse, best_w = float("inf"), [0.25]*4
    vals = np.arange(0.0, 1.01, 0.05)
    for w0 in vals:
        for w1 in vals:
            for w2 in vals:
                w3 = round(1.0 - w0 - w1 - w2, 6)
                if w3 < -1e-6: continue
                w3 = max(0.0, w3)
                ens = w0*oofs[0] + w1*oofs[1] + w2*oofs[2] + w3*oofs[3]
                rmse = float(np.sqrt(mean_squared_error(y, np.clip(ens, 0, None))))
                if rmse < best_rmse:
                    best_rmse, best_w = rmse, [w0, w1, w2, w3]
    print(f"  KFold RMSE (KFold-optimized weights) = {best_rmse:.4f}")
    print(f"  best weights: k30={best_w[0]:.2f} k200={best_w[1]:.2f} lgbm={best_w[2]:.2f} xgb={best_w[3]:.2f}")
    results.append({"model": "ensemble4_kfold_weights", "kfold_rmse": best_rmse,
                    "known_cv": 16.42, "known_cv_type": "loso", "public_lb": 26.11})

    # ── Summary ───────────────────────────────────────────────────────────
    results_df = pd.DataFrame(results)
    results_df.to_csv(EXPERIMENT_DIR / "results.csv", index=False, encoding="utf-8")

    print("\n" + "="*70)
    print("=== CV vs LB 乖離サマリ ===")
    print("="*70)
    print(f"{'model':<35} {'cv_type':<8} {'orig_cv':>8} {'kfold':>8} {'public_lb':>10} {'gap(kf-lb)':>11}")
    print("-"*70)
    for _, row in results_df.iterrows():
        lb   = row["public_lb"] if pd.notna(row["public_lb"]) else float("nan")
        gap  = row["kfold_rmse"] - lb if pd.notna(row["public_lb"]) else float("nan")
        orig = row["known_cv"] if pd.notna(row["known_cv"]) else float("nan")
        print(f"{row['model']:<35} {row['known_cv_type']:<8} {orig:>8.2f} {row['kfold_rmse']:>8.4f} {lb:>10.2f} {gap:>11.4f}")

    print(f"\nsaved → {EXPERIMENT_DIR / 'results.csv'}")


if __name__ == "__main__":
    main()
