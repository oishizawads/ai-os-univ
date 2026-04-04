"""
過去に負値でskipされた全実験をclip(0)して再評価・submission生成。
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from sklearn.cross_decomposition import PLSRegression
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge, Lasso, ARDRegression, HuberRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler

from _base_band2 import (
    load_data, select_band2, apply_snv, apply_snv_sg1,
    save_submission, SUBMISSIONS_DIR, EPS
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ─── helpers ─────────────────────────────────────────────────────────────────

def loso_oof_and_test(X, y, groups, X_test, preproc_fn, build_fn):
    """LOSO OOF + full-train test prediction, both raw (no clip)."""
    logo = LeaveOneGroupOut()
    Xp = preproc_fn(X)
    Xp_test = preproc_fn(X_test)
    oof = np.zeros_like(y, dtype=np.float64)
    for tr, val in logo.split(Xp, y, groups):
        m = build_fn(Xp[tr], y[tr])
        oof[val] = m.predict(Xp[val])
    m_full = build_fn(Xp, y)
    test_preds = m_full.predict(Xp_test)
    return oof, test_preds


def report(name, oof, test_preds, y, test_df, sample_submit_df, sample_col, tag):
    rmse_raw  = float(np.sqrt(mean_squared_error(y, oof)))
    rmse_clip = float(np.sqrt(mean_squared_error(y, np.clip(oof, 0, None))))
    neg_oof   = int(np.sum(oof < 0))
    neg_test  = int(np.sum(test_preds < 0))
    preds_clip = np.clip(test_preds, 0, None)
    out_path = SUBMISSIONS_DIR / f"{tag}_clip_submission.csv"
    save_submission(sample_submit_df, test_df, sample_col, preds_clip, out_path)
    print(f"[{name}]")
    print(f"  oof_neg={neg_oof}  loso_raw={rmse_raw:.4f}  loso_clip={rmse_clip:.4f}  delta={rmse_clip-rmse_raw:+.4f}")
    print(f"  test_neg={neg_test}  saved={out_path.name}")
    return dict(name=name, loso_raw=rmse_raw, loso_clip=rmse_clip, oof_neg=neg_oof, test_neg=neg_test)


# ─── LocalPLS helpers (copied from expLocalPLS_band2/train.py) ────────────────

BAND2_RANGE = (4800.0, 5350.0)

def normalize_rows(X):
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.clip(norms, 1e-12, None)

def predict_local_pls(X_train, y_train, X_query, k, n_comp):
    k_eff = min(k, len(X_train))
    X_tr_n = normalize_rows(X_train); X_q_n = normalize_rows(X_query)
    sims = X_q_n @ X_tr_n.T
    topk = np.argpartition(-sims, kth=k_eff-1, axis=1)[:, :k_eff]
    preds = []
    for i, idx in enumerate(topk):
        idx = idx[np.argsort(-sims[i, idx])]
        X_loc = X_train[idx]; y_loc = y_train[idx]
        mc = min(n_comp, X_loc.shape[0]-1, X_loc.shape[1])
        if mc < 1: preds.append(float(np.mean(y_loc))); continue
        m = PLSRegression(n_components=mc, max_iter=500)
        m.fit(X_loc, y_loc)
        preds.append(float(m.predict(X_query[i:i+1]).ravel()[0]))
    return np.array(preds, dtype=np.float64)

def apply_preproc_localpls(X, method):
    X = X.astype(np.float64, copy=True)
    if method == "raw": return X
    mu = X.mean(axis=1, keepdims=True); sd = np.clip(X.std(axis=1, keepdims=True), EPS, None)
    X = (X - mu) / sd
    if method == "snv": return X
    if method == "snv_sg1": return savgol_filter(X, window_length=11, polyorder=2, deriv=1, axis=1)
    raise ValueError(method)


# ─── main ────────────────────────────────────────────────────────────────────

def main():
    train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col = load_data()
    band2_cols = select_band2(wave_cols)
    X = train_df[band2_cols].to_numpy(dtype=np.float64)
    y = train_df[target_col].to_numpy(dtype=np.float64)
    groups = train_df[species_col].to_numpy()
    X_test = test_df[band2_cols].to_numpy(dtype=np.float64)
    logo = LeaveOneGroupOut()
    results = []

    # ── 1. LocalPLS band2 k=30 (LOSO raw=18.039, pred_min=-0.70) ─────────────
    print("\n[1] LocalPLS band2 k=30 n=3 snv_sg1")
    preproc = "snv_sg1"; k = 30; n_comp = 3
    Xp = apply_preproc_localpls(X, preproc)
    Xp_test = apply_preproc_localpls(X_test, preproc)
    oof = np.zeros_like(y, dtype=np.float64)
    for tr, val in logo.split(Xp, y, groups):
        oof[val] = predict_local_pls(Xp[tr], y[tr], Xp[val], k, n_comp)
    test_preds = predict_local_pls(Xp, y, Xp_test, k, n_comp)
    results.append(report("LocalPLS_band2_k30_n3", oof, test_preds, y,
                           test_df, sample_submit_df, sample_col, "localpls_band2_k30_n3"))

    # ── 2. PCR band2 snv n=30 alpha=0.01 (LOSO raw=19.69, 14 neg) ─────────────
    print("\n[2] PCR band2 snv n=30 alpha=0.01")
    def build_pcr(Xtr, ytr, pca_n=30, alpha=0.01):
        pca = PCA(n_components=pca_n, random_state=42)
        Xp2 = pca.fit_transform(Xtr)
        ridge = Ridge(alpha=alpha); ridge.fit(Xp2, ytr)
        class W:
            def __init__(self, pca, ridge): self.pca, self.ridge = pca, ridge
            def predict(self, X): return self.ridge.predict(self.pca.transform(X))
        return W(pca, ridge)
    oof, test_preds = loso_oof_and_test(X, y, groups, X_test, apply_snv, build_pcr)
    results.append(report("PCR_snv_n30_a0.01", oof, test_preds, y,
                           test_df, sample_submit_df, sample_col, "pcr_snv_n30_a001"))

    # ── 3. ElasticNet sg1 lasso 1e-2 (already done, re-confirm) ──────────────
    # Already handled in check_clip_all.py, skip re-run

    # ── 4. RGF snv pca20 (LOSO raw=23.23, 13 neg) ─────────────────────────────
    print("\n[4] RGF snv pca20")
    try:
        from rgf.sklearn import RGFRegressor
        def build_rgf(Xtr, ytr, pca_n=20):
            pca = PCA(n_components=pca_n, random_state=42)
            Xp2 = pca.fit_transform(Xtr)
            m = RGFRegressor(max_leaf=500, algorithm="RGF", loss="LS", n_iter=10)
            m.fit(Xp2, ytr)
            class W:
                def __init__(self, pca, m): self.pca, self.m = pca, m
                def predict(self, X): return self.m.predict(self.pca.transform(X))
            return W(pca, m)
        oof, test_preds = loso_oof_and_test(X, y, groups, X_test, apply_snv, build_rgf)
        results.append(report("RGF_snv_pca20", oof, test_preds, y,
                               test_df, sample_submit_df, sample_col, "rgf_snv_pca20"))
    except Exception as e:
        print(f"  RGF skipped: {e}")

    # ── 5. Huber snv pca20 e=2 (LOSO raw=19.66, 36 neg) ──────────────────────
    print("\n[5] Huber snv pca20 epsilon=2")
    def build_huber(Xtr, ytr, pca_n=20, epsilon=2.0):
        pca = PCA(n_components=pca_n, random_state=42)
        Xp2 = pca.fit_transform(Xtr)
        sc = StandardScaler(); Xs = sc.fit_transform(Xp2)
        m = HuberRegressor(epsilon=epsilon, max_iter=300); m.fit(Xs, ytr)
        class W:
            def __init__(self, pca, sc, m): self.pca, self.sc, self.m = pca, sc, m
            def predict(self, X): return self.m.predict(self.sc.transform(self.pca.transform(X)))
        return W(pca, sc, m)
    oof, test_preds = loso_oof_and_test(X, y, groups, X_test, apply_snv, build_huber)
    results.append(report("Huber_snv_pca20_e2", oof, test_preds, y,
                           test_df, sample_submit_df, sample_col, "huber_snv_pca20_e2"))

    # ── 6. ARD snv pca20 (LOSO raw=19.84, 53 neg) ────────────────────────────
    print("\n[6] ARD snv pca20")
    def build_ard(Xtr, ytr, pca_n=20):
        pca = PCA(n_components=pca_n, random_state=42)
        Xp2 = pca.fit_transform(Xtr)
        sc = StandardScaler(); Xs = sc.fit_transform(Xp2)
        m = ARDRegression(max_iter=300); m.fit(Xs, ytr)
        class W:
            def __init__(self, pca, sc, m): self.pca, self.sc, self.m = pca, sc, m
            def predict(self, X): return self.m.predict(self.sc.transform(self.pca.transform(X)))
        return W(pca, sc, m)
    oof, test_preds = loso_oof_and_test(X, y, groups, X_test, apply_snv, build_ard)
    results.append(report("ARD_snv_pca20", oof, test_preds, y,
                           test_df, sample_submit_df, sample_col, "ard_snv_pca20"))

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n=== CLIP SUMMARY ===")
    df = pd.DataFrame(results).sort_values("loso_clip")
    print(df.to_string(index=False))
    df.to_csv(Path(__file__).parent / "clip_all_results.csv", index=False, encoding="utf-8")


if __name__ == "__main__":
    main()
