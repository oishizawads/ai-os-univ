"""
expA054_ensemble_optuna
LocalPLS_k30 + LocalPLS_k200 + LGBM_optuna + XGB_optuna の4モデルアンサンブル。
Optuna best params は expA053_optuna_all から読み込む。
OOF重み探索 (step=0.05) + fine search (step=0.01)。
"""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut
from scipy.signal import savgol_filter
from sklearn.cross_decomposition import PLSRegression

from _base_band2 import (
    load_data, select_band2, apply_snv, apply_snv_sg1,
    save_submission, SUBMISSIONS_DIR, EPS,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT   = Path(__file__).resolve().parents[2]
EXPERIMENT_DIR = Path(__file__).resolve().parent
RESULTS_PATH   = EXPERIMENT_DIR / "results.csv"
A053_PARAMS    = PROJECT_ROOT / "experiments" / "expA053_optuna_all" / "best_params"
LOCALPLS_DIR   = PROJECT_ROOT / "experiments" / "expLocalPLS_band2"

SEED = 42


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


def run_localpls_loso(X, y, groups, k, n_comp):
    logo = LeaveOneGroupOut()
    oof  = np.zeros_like(y, dtype=np.float64)
    for fold, (tr, val) in enumerate(logo.split(X, y, groups), 1):
        oof[val] = predict_local_pls(X[tr], y[tr], X[val], k, n_comp)
        rmse = float(np.sqrt(mean_squared_error(y[val], oof[val])))
        print(f"    fold={fold:2d}  rmse={rmse:.4f}")
    return oof


# ---------------------------------------------------------------------------
# Weight search helpers
# ---------------------------------------------------------------------------

def ensemble_rmse(oofs: list[np.ndarray], weights: list[float], y: np.ndarray) -> float:
    pred = sum(w * o for w, o in zip(weights, oofs))
    return float(np.sqrt(mean_squared_error(y, np.clip(pred, 0, None))))


def search_weights(oofs: list[np.ndarray], y: np.ndarray, step: float = 0.05):
    """Grid search over simplex for N models."""
    n = len(oofs)
    best_rmse = float("inf")
    best_w    = [1 / n] * n

    def recurse(idx, remaining, current):
        nonlocal best_rmse, best_w
        if idx == n - 1:
            w = current + [remaining]
            rmse = ensemble_rmse(oofs, w, y)
            if rmse < best_rmse:
                best_rmse, best_w = rmse, w[:]
            return
        vals = np.arange(0.0, remaining + step / 2, step)
        for v in vals:
            recurse(idx + 1, round(remaining - v, 8), current + [round(v, 8)])

    recurse(0, 1.0, [])
    return best_w, best_rmse


def fine_search_weights(oofs, y, coarse_w, radius=0.1, step=0.01):
    n = len(oofs)
    best_rmse = ensemble_rmse(oofs, coarse_w, y)
    best_w    = coarse_w[:]

    def recurse(idx, remaining, current):
        nonlocal best_rmse, best_w
        if idx == n - 1:
            w = current + [remaining]
            if any(v < -1e-9 for v in w):
                return
            w = [max(0.0, v) for v in w]
            rmse = ensemble_rmse(oofs, w, y)
            if rmse < best_rmse:
                best_rmse, best_w = rmse, w[:]
            return
        lo = max(0.0, coarse_w[idx] - radius)
        hi = min(1.0, coarse_w[idx] + radius)
        for v in np.arange(lo, hi + step / 2, step):
            recurse(idx + 1, round(remaining - v, 8), current + [round(v, 8)])

    recurse(0, 1.0, [])
    return best_w, best_rmse


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)

    train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col = load_data()
    band2_cols = select_band2(wave_cols)
    X_raw      = train_df[band2_cols].to_numpy(dtype=np.float64)
    y          = train_df[target_col].to_numpy(dtype=np.float64)
    groups     = train_df[species_col].to_numpy()
    X_test_raw = test_df[band2_cols].to_numpy(dtype=np.float64)

    X_snv      = apply_snv(X_raw)
    X_sg1      = apply_snv_sg1(X_raw)
    X_snv_test = apply_snv(X_test_raw)
    X_sg1_test = apply_snv_sg1(X_test_raw)

    print(f"band2_features={len(band2_cols)}  n_train={len(y)}  n_species={len(np.unique(groups))}")

    # ── A: LocalPLS k=30 snv_sg1 ──────────────────────────────────────────────
    oof_a_path = LOCALPLS_DIR / "oof_k30_predictions.csv"
    if oof_a_path.exists():
        print("\n[A] LocalPLS k=30 snv_sg1  (loading saved OOF)")
        oof_a = pd.read_csv(oof_a_path)["oof_pred"].to_numpy(dtype=np.float64)
    else:
        print("\n[A] LocalPLS k=30 snv_sg1  (running LOSO)")
        oof_a = run_localpls_loso(X_sg1, y, groups, k=30, n_comp=3)
    rmse_a = float(np.sqrt(mean_squared_error(y, np.clip(oof_a, 0, None))))
    print(f"  LOSO RMSE = {rmse_a:.4f}")

    # ── B: LocalPLS k=200 snv_sg1 ─────────────────────────────────────────────
    oof_b_path = LOCALPLS_DIR / "oof_predictions.csv"
    if oof_b_path.exists():
        print("\n[B] LocalPLS k=200 snv_sg1  (loading saved OOF)")
        oof_b = pd.read_csv(oof_b_path)["oof_pred"].to_numpy(dtype=np.float64)
    else:
        print("\n[B] LocalPLS k=200 snv_sg1  (running LOSO)")
        oof_b = run_localpls_loso(X_sg1, y, groups, k=200, n_comp=3)
    rmse_b = float(np.sqrt(mean_squared_error(y, np.clip(oof_b, 0, None))))
    print(f"  LOSO RMSE = {rmse_b:.4f}")

    # ── C: LGBM snv (Optuna best params) ──────────────────────────────────────
    lgbm_p = json.loads((A053_PARAMS / "lgbm_snv.json").read_text())
    lgbm_params = dict(
        objective="regression", metric="rmse", verbose=-1,
        n_jobs=-1, random_state=SEED, subsample_freq=1, **lgbm_p,
    )
    print("\n[C] LGBM snv (Optuna)  running LOSO ...")
    logo = LeaveOneGroupOut()
    oof_c = np.zeros_like(y, dtype=np.float64)
    for fold, (tr, val) in enumerate(logo.split(X_snv, y, groups), 1):
        m = LGBMRegressor(**lgbm_params)
        m.fit(X_snv[tr], y[tr])
        oof_c[val] = m.predict(X_snv[val])
        print(f"    fold={fold:2d}  rmse={np.sqrt(mean_squared_error(y[val], oof_c[val])):.4f}")
    rmse_c = float(np.sqrt(mean_squared_error(y, np.clip(oof_c, 0, None))))
    print(f"  LOSO RMSE = {rmse_c:.4f}")

    # ── D: XGB snv (Optuna best params) ───────────────────────────────────────
    xgb_p = json.loads((A053_PARAMS / "xgb_snv.json").read_text())
    xgb_params = dict(
        objective="reg:squarederror", verbosity=0,
        random_state=SEED, n_jobs=-1, tree_method="hist", **xgb_p,
    )
    print("\n[D] XGB snv (Optuna)  running LOSO ...")
    oof_d = np.zeros_like(y, dtype=np.float64)
    for fold, (tr, val) in enumerate(logo.split(X_snv, y, groups), 1):
        m = XGBRegressor(**xgb_params)
        m.fit(X_snv[tr], y[tr])
        oof_d[val] = m.predict(X_snv[val])
        print(f"    fold={fold:2d}  rmse={np.sqrt(mean_squared_error(y[val], oof_d[val])):.4f}")
    rmse_d = float(np.sqrt(mean_squared_error(y, np.clip(oof_d, 0, None))))
    print(f"  LOSO RMSE = {rmse_d:.4f}")

    # ── Save OOF predictions ───────────────────────────────────────────────────
    oof_df = pd.DataFrame({
        "sample_number": train_df[sample_col].to_numpy(),
        "true_mc": y,
        "local_pls_k30":  oof_a,
        "local_pls_k200": oof_b,
        "lgbm_snv":       oof_c,
        "xgb_snv":        oof_d,
    })
    oof_df.to_csv(EXPERIMENT_DIR / "oof_all.csv", index=False, encoding="utf-8")
    print(f"\nSaved OOF → oof_all.csv")

    # ── Ensemble experiments ───────────────────────────────────────────────────
    oofs_all = [oof_a, oof_b, oof_c, oof_d]
    labels   = ["local_pls_k30", "local_pls_k200", "lgbm_snv", "xgb_snv"]

    all_results = []

    # 3-model combos
    from itertools import combinations
    for combo in combinations(range(4), 3):
        sub_oofs   = [oofs_all[i] for i in combo]
        sub_labels = [labels[i]   for i in combo]
        w_coarse, rmse_coarse = search_weights(sub_oofs, y, step=0.05)
        w_fine,   rmse_fine   = fine_search_weights(sub_oofs, y, w_coarse, radius=0.1, step=0.01)
        row = {"models": "+".join(sub_labels), "n_models": 3, "loso_rmse": rmse_fine}
        for lbl, wv in zip(sub_labels, w_fine):
            row[f"w_{lbl}"] = round(wv, 4)
        all_results.append(row)
        print(f"  3-model {'+'.join(sub_labels[:2])}... RMSE={rmse_fine:.4f}  weights={[round(v,3) for v in w_fine]}")

    # 4-model
    w_coarse, rmse_coarse = search_weights(oofs_all, y, step=0.05)
    w_fine,   rmse_fine   = fine_search_weights(oofs_all, y, w_coarse, radius=0.1, step=0.01)
    row = {"models": "+".join(labels), "n_models": 4, "loso_rmse": rmse_fine}
    for lbl, wv in zip(labels, w_fine):
        row[f"w_{lbl}"] = round(wv, 4)
    all_results.append(row)
    print(f"\n  4-model ensemble RMSE={rmse_fine:.4f}  weights={[round(v,3) for v in w_fine]}")

    results_df = pd.DataFrame(all_results).sort_values("loso_rmse").reset_index(drop=True)
    results_df["rmse_local_pls_k30"]  = rmse_a
    results_df["rmse_local_pls_k200"] = rmse_b
    results_df["rmse_lgbm_snv"]       = rmse_c
    results_df["rmse_xgb_snv"]        = rmse_d
    results_df.to_csv(RESULTS_PATH, index=False, encoding="utf-8")

    print("\n=== Ensemble Results ===")
    print(results_df[["models", "loso_rmse"]].to_string(index=False))
    print(f"\nsaved → {RESULTS_PATH}")

    # ── Best ensemble test prediction ──────────────────────────────────────────
    best_row = results_df.iloc[0]
    best_models_str = best_row["models"]
    best_combo_labels = best_models_str.split("+")
    best_weights_map  = {lbl: best_row.get(f"w_{lbl}", 0.0) for lbl in best_combo_labels}
    print(f"\n[Best ensemble] {best_models_str}  RMSE={best_row['loso_rmse']:.4f}")
    print(f"  weights: {best_weights_map}")

    print("\n[Test predictions]")
    # full-train fit for each model needed
    test_preds = {}

    # LocalPLS k=30
    if "local_pls_k30" in best_combo_labels:
        test_preds["local_pls_k30"] = predict_local_pls(X_sg1, y, X_sg1_test, k=30, n_comp=3)

    # LocalPLS k=200
    if "local_pls_k200" in best_combo_labels:
        test_preds["local_pls_k200"] = predict_local_pls(X_sg1, y, X_sg1_test, k=200, n_comp=3)

    # LGBM
    if "lgbm_snv" in best_combo_labels:
        m = LGBMRegressor(**lgbm_params)
        m.fit(X_snv, y)
        test_preds["lgbm_snv"] = m.predict(X_snv_test)

    # XGB
    if "xgb_snv" in best_combo_labels:
        m = XGBRegressor(**xgb_params)
        m.fit(X_snv, y)
        test_preds["xgb_snv"] = m.predict(X_snv_test)

    # Also save individual submissions
    for lbl, preds in test_preds.items():
        sub_path = SUBMISSIONS_DIR / f"expA054_{lbl}_submission.csv"
        save_submission(sample_submit_df, test_df, sample_col, np.clip(preds, 0, None), sub_path)

    # Best ensemble submission
    ens_pred = sum(best_weights_map[lbl] * test_preds[lbl] for lbl in best_combo_labels)
    ens_pred = np.clip(ens_pred, 0, None)
    tag = "_".join(f"{lbl[:4]}{best_weights_map[lbl]:.2f}" for lbl in best_combo_labels)
    sub_path = SUBMISSIONS_DIR / f"expA054_best_ensemble_{tag}_submission.csv"
    save_submission(sample_submit_df, test_df, sample_col, ens_pred, sub_path)
    print(f"  saved → {sub_path.name}")

    # Also save 4-model submission regardless of best
    w_4 = [best_row.get(f"w_{lbl}", 0.0) for lbl in labels] if best_row["n_models"] == 4 else w_fine
    if "4-model" not in best_models_str:
        # re-do 4-model test prediction
        t4 = np.zeros(len(test_df), dtype=np.float64)
        for lbl, w4v in zip(labels, w_fine):
            if lbl not in test_preds:
                if "pls_k30" in lbl:
                    test_preds[lbl] = predict_local_pls(X_sg1, y, X_sg1_test, k=30, n_comp=3)
                elif "pls_k200" in lbl:
                    test_preds[lbl] = predict_local_pls(X_sg1, y, X_sg1_test, k=200, n_comp=3)
                elif "lgbm" in lbl:
                    m = LGBMRegressor(**lgbm_params); m.fit(X_snv, y)
                    test_preds[lbl] = m.predict(X_snv_test)
                elif "xgb" in lbl:
                    m = XGBRegressor(**xgb_params); m.fit(X_snv, y)
                    test_preds[lbl] = m.predict(X_snv_test)
            t4 += w4v * test_preds[lbl]
        t4 = np.clip(t4, 0, None)
        sub4 = SUBMISSIONS_DIR / f"expA054_4model_ensemble_submission.csv"
        save_submission(sample_submit_df, test_df, sample_col, t4, sub4)
        print(f"  saved 4-model → {sub4.name}")

    print(f"\n=== DONE ===")
    print(f"Best ensemble LOSO RMSE = {best_row['loso_rmse']:.4f}")
    print(f"Previous best (expA046) = 16.6236")


if __name__ == "__main__":
    main()
