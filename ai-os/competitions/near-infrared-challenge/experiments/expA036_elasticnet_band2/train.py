from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNet, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut
from _base_band2 import load_data, select_band2, apply_snv, apply_snv_sg1, save_submission, SUBMISSIONS_DIR

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

EXPERIMENT_DIR = Path(__file__).resolve().parent
RESULTS_PATH = EXPERIMENT_DIR / "results.csv"

SETTINGS = [
    ("snv_lasso_1e-2",    apply_snv,     "lasso",  {"alpha": 0.01, "max_iter": 10000}),
    ("snv_lasso_1e-1",    apply_snv,     "lasso",  {"alpha": 0.1,  "max_iter": 10000}),
    ("snv_lasso_1.0",     apply_snv,     "lasso",  {"alpha": 1.0,  "max_iter": 10000}),
    ("snv_en_a1e-1_l0.5", apply_snv,     "enet",   {"alpha": 0.1,  "l1_ratio": 0.5,  "max_iter": 10000}),
    ("snv_en_a1e-1_l0.1", apply_snv,     "enet",   {"alpha": 0.1,  "l1_ratio": 0.1,  "max_iter": 10000}),
    ("snv_en_a1.0_l0.5",  apply_snv,     "enet",   {"alpha": 1.0,  "l1_ratio": 0.5,  "max_iter": 10000}),
    ("sg1_lasso_1e-2",    apply_snv_sg1, "lasso",  {"alpha": 0.01, "max_iter": 10000}),
    ("sg1_en_a1e-1_l0.5", apply_snv_sg1, "enet",   {"alpha": 0.1,  "l1_ratio": 0.5,  "max_iter": 10000}),
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
    best_rmse, best_cfg = float("inf"), None

    for name, preproc_fn, mtype, params in SETTINGS:
        Xp = preproc_fn(X)
        oof = np.zeros_like(y, dtype=np.float64)
        for fold, (tr, val) in enumerate(logo.split(Xp, y, groups), 1):
            sc = StandardScaler()
            X_tr = sc.fit_transform(Xp[tr])
            X_val = sc.transform(Xp[val])
            m = Lasso(**params) if mtype == "lasso" else ElasticNet(**params)
            m.fit(X_tr, y[tr])
            oof[val] = m.predict(X_val)
            print(f"  [{name}] fold={fold} holdout={np.unique(groups[val]).tolist()} rmse={np.sqrt(mean_squared_error(y[val], oof[val])):.4f}")
        rmse = float(np.sqrt(mean_squared_error(y, oof)))
        results.append({"setting": name, "loso_rmse": rmse})
        print(f"[{name}] LOSO={rmse:.6f}\n")
        if rmse < best_rmse:
            best_rmse, best_cfg = rmse, (name, preproc_fn, mtype, params)

    pd.DataFrame(results).sort_values("loso_rmse").to_csv(RESULTS_PATH, index=False, encoding="utf-8")
    print(pd.DataFrame(results).sort_values("loso_rmse").to_string(index=False))

    name, preproc_fn, mtype, params = best_cfg
    Xp_all = preproc_fn(X)
    Xp_test = preproc_fn(X_test)
    sc = StandardScaler()
    X_tr = sc.fit_transform(Xp_all)
    X_test_sc = sc.transform(Xp_test)
    m = Lasso(**params) if mtype == "lasso" else ElasticNet(**params)
    m.fit(X_tr, y)
    preds = m.predict(X_test_sc)
    print(f"\nbest={name} loso={best_rmse:.6f} pred_min={preds.min():.4f} pred_max={preds.max():.4f}")
    if np.any(preds < 0):
        print(f"negatives={np.sum(preds<0)}, submission_skipped=True"); return
    save_submission(sample_submit_df, test_df, sample_col, preds, SUBMISSIONS_DIR / f"expA036_elasticnet_{name}_submission.csv")
    print(f"saved_submission=expA036_elasticnet_{name}_submission.csv")

if __name__ == "__main__":
    main()
