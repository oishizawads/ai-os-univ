from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut
from _base_band2 import load_data, select_band2, apply_snv, apply_snv_sg1, save_submission, SUBMISSIONS_DIR
from sklearn.decomposition import PCA

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

EXPERIMENT_DIR = Path(__file__).resolve().parent
RESULTS_PATH = EXPERIMENT_DIR / "results.csv"

# SVR is O(n^2~3), reduce dim with PCA first
SETTINGS = [
    ("snv_pca20_svr_rbf",  apply_snv,     20, {"kernel": "rbf",    "C": 10.0,  "epsilon": 0.1, "gamma": "scale"}),
    ("snv_pca20_svr_rbf2", apply_snv,     20, {"kernel": "rbf",    "C": 100.0, "epsilon": 0.1, "gamma": "scale"}),
    ("snv_sg1_pca20_svr",  apply_snv_sg1, 20, {"kernel": "rbf",    "C": 10.0,  "epsilon": 0.1, "gamma": "scale"}),
    ("snv_pca20_svr_poly", apply_snv,     20, {"kernel": "poly",   "C": 10.0,  "epsilon": 0.1, "degree": 3}),
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

    results = []
    best_rmse, best_name, best_preproc_fn, best_pca_n, best_params = float("inf"), None, None, None, None

    for name, preproc_fn, pca_n, params in SETTINGS:
        Xp = preproc_fn(X)
        oof = np.zeros_like(y, dtype=np.float64)
        for fold, (tr, val) in enumerate(logo.split(Xp, y, groups), 1):
            pca = PCA(n_components=pca_n, random_state=42)
            X_tr_pca = pca.fit_transform(Xp[tr])
            X_val_pca = pca.transform(Xp[val])
            sc = StandardScaler()
            X_tr_sc = sc.fit_transform(X_tr_pca)
            X_val_sc = sc.transform(X_val_pca)
            m = SVR(**params)
            m.fit(X_tr_sc, y[tr])
            oof[val] = m.predict(X_val_sc)
            print(f"  [{name}] fold={fold} holdout={np.unique(groups[val]).tolist()} rmse={np.sqrt(mean_squared_error(y[val], oof[val])):.4f}")
        rmse = float(np.sqrt(mean_squared_error(y, oof)))
        results.append({"setting": name, "loso_rmse": rmse})
        print(f"[{name}] LOSO={rmse:.6f}\n")
        if rmse < best_rmse:
            best_rmse, best_name, best_preproc_fn, best_pca_n, best_params = rmse, name, preproc_fn, pca_n, params

    pd.DataFrame(results).sort_values("loso_rmse").to_csv(RESULTS_PATH, index=False, encoding="utf-8")
    print(pd.DataFrame(results).sort_values("loso_rmse").to_string(index=False))

    Xp_all = best_preproc_fn(X)
    Xp_test = best_preproc_fn(X_test)
    pca_f = PCA(n_components=best_pca_n, random_state=42)
    X_tr_pca = pca_f.fit_transform(Xp_all)
    X_test_pca = pca_f.transform(Xp_test)
    sc_f = StandardScaler()
    X_tr_sc = sc_f.fit_transform(X_tr_pca)
    X_test_sc = sc_f.transform(X_test_pca)
    m = SVR(**best_params)
    m.fit(X_tr_sc, y)
    preds = m.predict(X_test_sc)
    print(f"\nbest={best_name} loso={best_rmse:.6f} pred_min={preds.min():.4f} pred_max={preds.max():.4f}")
    if np.any(preds < 0):
        print(f"negatives={np.sum(preds<0)}, submission_skipped=True"); return
    save_submission(sample_submit_df, test_df, sample_col, preds, SUBMISSIONS_DIR / f"expA035_svr_{best_name}_submission.csv")
    print(f"saved_submission=expA035_svr_{best_name}_submission.csv")

if __name__ == "__main__":
    main()
