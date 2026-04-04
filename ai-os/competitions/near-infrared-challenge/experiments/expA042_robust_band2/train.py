from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from sklearn.linear_model import HuberRegressor, RANSACRegressor, TheilSenRegressor
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut
from _base_band2 import load_data, select_band2, apply_snv, apply_snv_sg1, save_submission, SUBMISSIONS_DIR
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")

EXPERIMENT_DIR = Path(__file__).resolve().parent
RESULTS_PATH = EXPERIMENT_DIR / "results.csv"

SETTINGS = [
    ("snv_pca20_huber",       apply_snv,     20, "huber",  {"epsilon":1.35, "max_iter":300}),
    ("snv_sg1_pca20_huber",   apply_snv_sg1, 20, "huber",  {"epsilon":1.35, "max_iter":300}),
    ("snv_pca20_huber_e2",    apply_snv,     20, "huber",  {"epsilon":2.0,  "max_iter":300}),
    ("snv_pca20_ransac",      apply_snv,     20, "ransac", {"random_state":42}),
]

def main():
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
    train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col = load_data()
    band2_cols = select_band2(wave_cols)
    X = train_df[band2_cols].to_numpy(dtype=np.float64); y = train_df[target_col].to_numpy(dtype=np.float64)
    groups = train_df[species_col].to_numpy(); X_test = test_df[band2_cols].to_numpy(dtype=np.float64)
    logo = LeaveOneGroupOut()
    results = []; best_rmse, best_cfg = float("inf"), None
    for name, pfn, pca_n, mtype, params in SETTINGS:
        Xp = pfn(X); oof = np.zeros_like(y, dtype=np.float64)
        for fold, (tr, val) in enumerate(logo.split(Xp, y, groups), 1):
            pca = PCA(n_components=pca_n, random_state=42)
            Xtr = pca.fit_transform(Xp[tr]); Xval = pca.transform(Xp[val])
            sc = StandardScaler(); Xtr = sc.fit_transform(Xtr); Xval = sc.transform(Xval)
            if mtype == "huber": m = HuberRegressor(**params)
            elif mtype == "ransac": m = RANSACRegressor(**params)
            else: m = TheilSenRegressor(**params)
            m.fit(Xtr, y[tr]); oof[val] = m.predict(Xval)
            print(f"  [{name}] fold={fold} holdout={np.unique(groups[val]).tolist()} rmse={np.sqrt(mean_squared_error(y[val], oof[val])):.4f}")
        rmse = float(np.sqrt(mean_squared_error(y, oof)))
        results.append({"setting": name, "loso_rmse": rmse}); print(f"[{name}] LOSO={rmse:.6f}\n")
        if rmse < best_rmse: best_rmse, best_cfg = rmse, (name, pfn, pca_n, mtype, params)
    pd.DataFrame(results).sort_values("loso_rmse").to_csv(RESULTS_PATH, index=False, encoding="utf-8")
    print(pd.DataFrame(results).sort_values("loso_rmse").to_string(index=False))
    name, pfn, pca_n, mtype, params = best_cfg
    Xp_all = pfn(X); Xp_test = pfn(X_test)
    pca = PCA(n_components=pca_n, random_state=42); Xtr = pca.fit_transform(Xp_all); Xtest = pca.transform(Xp_test)
    sc = StandardScaler(); Xtr = sc.fit_transform(Xtr); Xtest = sc.transform(Xtest)
    if mtype == "huber": m = HuberRegressor(**params)
    elif mtype == "ransac": m = RANSACRegressor(**params)
    else: m = TheilSenRegressor(**params)
    m.fit(Xtr, y); preds = m.predict(Xtest)
    print(f"\nbest={name} loso={best_rmse:.6f} min={preds.min():.4f} max={preds.max():.4f}")
    if np.any(preds < 0): print(f"negatives={np.sum(preds<0)}, submission_skipped=True"); return
    save_submission(sample_submit_df, test_df, sample_col, preds, SUBMISSIONS_DIR/f"expA042_robust_{name}_submission.csv")
    print(f"saved_submission=expA042_robust_{name}_submission.csv")

if __name__ == "__main__": main()
