"""
負値があってskipされた実験の test predictions をclip(0)して再保存し、
OOF clip後のLOSO RMSEも出力する。
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Lasso, ElasticNet, HuberRegressor, ARDRegression
from scipy.signal import savgol_filter

from _base_band2 import (
    load_data, select_band2, apply_snv, apply_snv_sg1,
    save_submission, SUBMISSIONS_DIR, EPS
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def loso_predict(X, y, groups, preproc_fn, model_fn):
    """Returns oof predictions."""
    logo = LeaveOneGroupOut()
    Xp = preproc_fn(X)
    oof = np.zeros_like(y, dtype=np.float64)
    for tr, val in logo.split(Xp, y, groups):
        m = model_fn(Xp[tr], y[tr])
        oof[val] = m.predict(Xp[val]) if hasattr(m, "predict") else m(Xp[val])
    return oof


def make_model_elasticnet(alpha, l1_ratio=None):
    def fn(X_tr, y_tr):
        sc = StandardScaler()
        X_s = sc.fit_transform(X_tr)
        if l1_ratio is None:
            m = Lasso(alpha=alpha, max_iter=10000)
        else:
            m = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, max_iter=10000)
        m.fit(X_s, y_tr)
        class Wrapper:
            def __init__(self, m, sc): self.m, self.sc = m, sc
            def predict(self, X): return self.m.predict(self.sc.transform(X))
        return Wrapper(m, sc)
    return fn


def make_model_huber(epsilon):
    def fn(X_tr, y_tr, pca_n=20):
        pca = PCA(n_components=pca_n, random_state=42)
        Xp = pca.fit_transform(X_tr)
        sc = StandardScaler(); Xs = sc.fit_transform(Xp)
        m = HuberRegressor(epsilon=epsilon, max_iter=300); m.fit(Xs, y_tr)
        class Wrapper:
            def __init__(self, m, sc, pca): self.m, self.sc, self.pca = m, sc, pca
            def predict(self, X): return self.m.predict(self.sc.transform(self.pca.transform(X)))
        return Wrapper(m, sc, pca)
    return fn


def make_model_ard(pca_n=20):
    def fn(X_tr, y_tr):
        pca = PCA(n_components=pca_n, random_state=42)
        Xp = pca.fit_transform(X_tr)
        sc = StandardScaler(); Xs = sc.fit_transform(Xp)
        m = ARDRegression(max_iter=300); m.fit(Xs, y_tr)
        class Wrapper:
            def __init__(self, m, sc, pca): self.m, self.sc, self.pca = m, sc, pca
            def predict(self, X): return self.m.predict(self.sc.transform(self.pca.transform(X)))
        return Wrapper(m, sc, pca)
    return fn


def run_and_clip(name, preproc_fn, build_model_fn, X, y, groups, X_test,
                 train_df, test_df, sample_submit_df, sample_col):
    logo = LeaveOneGroupOut()
    Xp = preproc_fn(X)
    Xp_test = preproc_fn(X_test)
    oof = np.zeros_like(y, dtype=np.float64)
    for tr, val in logo.split(Xp, y, groups):
        m = build_model_fn(Xp[tr], y[tr])
        oof[val] = m.predict(Xp[val])

    # LOSO raw vs clipped
    rmse_raw   = float(np.sqrt(mean_squared_error(y, oof)))
    rmse_clip  = float(np.sqrt(mean_squared_error(y, np.clip(oof, 0, None))))
    neg_oof    = int(np.sum(oof < 0))

    # test prediction
    m_full = build_model_fn(Xp, y)
    preds = m_full.predict(Xp_test)
    neg_test = int(np.sum(preds < 0))
    preds_clip = np.clip(preds, 0, None)

    out_path = SUBMISSIONS_DIR / f"{name}_clip_submission.csv"
    save_submission(sample_submit_df, test_df, sample_col, preds_clip, out_path)

    print(f"[{name}]")
    print(f"  oof_neg={neg_oof}  loso_raw={rmse_raw:.4f}  loso_clip={rmse_clip:.4f}  delta={rmse_clip-rmse_raw:+.4f}")
    print(f"  test_neg={neg_test}  saved={out_path.name}")
    return {"name": name, "loso_raw": rmse_raw, "loso_clip": rmse_clip, "oof_neg": neg_oof, "test_neg": neg_test}


def main():
    train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col = load_data()
    band2_cols = select_band2(wave_cols)
    X = train_df[band2_cols].to_numpy(dtype=np.float64)
    y = train_df[target_col].to_numpy(dtype=np.float64)
    groups = train_df[species_col].to_numpy()
    X_test = test_df[band2_cols].to_numpy(dtype=np.float64)

    results = []

    # ElasticNet best: sg1_lasso_1e-2
    results.append(run_and_clip(
        "elasticnet_sg1_lasso_1e-2", apply_snv_sg1,
        lambda Xtr, ytr: make_model_elasticnet(0.01)(Xtr, ytr),
        X, y, groups, X_test, train_df, test_df, sample_submit_df, sample_col
    ))

    # Huber best: snv_pca20_huber_e2
    results.append(run_and_clip(
        "robust_snv_pca20_huber_e2", apply_snv,
        make_model_huber(2.0),
        X, y, groups, X_test, train_df, test_df, sample_submit_df, sample_col
    ))

    # ARD best: snv_pca20_ard
    results.append(run_and_clip(
        "bayesian_snv_pca20_ard", apply_snv,
        make_model_ard(20),
        X, y, groups, X_test, train_df, test_df, sample_submit_df, sample_col
    ))

    print("\n=== Summary ===")
    df = pd.DataFrame(results)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
