from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from sklearn.kernel_ridge import KernelRidge
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut
from _base_band2 import load_data, select_band2, apply_snv, apply_snv_sg1, save_submission, SUBMISSIONS_DIR
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")

EXPERIMENT_DIR = Path(__file__).resolve().parent
RESULTS_PATH = EXPERIMENT_DIR / "results.csv"

SETTINGS = [
    ("snv_pca20_kr_rbf_1",    apply_snv,     20, {"kernel":"rbf","alpha":1.0,  "gamma":None}),
    ("snv_pca20_kr_rbf_0.1",  apply_snv,     20, {"kernel":"rbf","alpha":0.1,  "gamma":None}),
    ("snv_pca30_kr_rbf_1",    apply_snv,     30, {"kernel":"rbf","alpha":1.0,  "gamma":None}),
    ("snv_sg1_pca20_kr_rbf",  apply_snv_sg1, 20, {"kernel":"rbf","alpha":1.0,  "gamma":None}),
    ("snv_pca20_kr_poly",     apply_snv,     20, {"kernel":"poly","alpha":1.0, "degree":3}),
]

def main():
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
    train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col = load_data()
    band2_cols = select_band2(wave_cols)
    X = train_df[band2_cols].to_numpy(dtype=np.float64); y = train_df[target_col].to_numpy(dtype=np.float64)
    groups = train_df[species_col].to_numpy(); X_test = test_df[band2_cols].to_numpy(dtype=np.float64)
    logo = LeaveOneGroupOut()
    results = []; best_rmse, best_cfg = float("inf"), None
    for name, pfn, pca_n, params in SETTINGS:
        Xp = pfn(X); oof = np.zeros_like(y, dtype=np.float64)
        for fold, (tr, val) in enumerate(logo.split(Xp, y, groups), 1):
            pca = PCA(n_components=pca_n, random_state=42)
            Xtr = pca.fit_transform(Xp[tr]); Xval = pca.transform(Xp[val])
            sc = StandardScaler(); Xtr = sc.fit_transform(Xtr); Xval = sc.transform(Xval)
            m = KernelRidge(**params); m.fit(Xtr, y[tr]); oof[val] = m.predict(Xval)
            print(f"  [{name}] fold={fold} holdout={np.unique(groups[val]).tolist()} rmse={np.sqrt(mean_squared_error(y[val], oof[val])):.4f}")
        rmse = float(np.sqrt(mean_squared_error(y, oof)))
        results.append({"setting": name, "loso_rmse": rmse}); print(f"[{name}] LOSO={rmse:.6f}\n")
        if rmse < best_rmse: best_rmse, best_cfg = rmse, (name, pfn, pca_n, params)
    pd.DataFrame(results).sort_values("loso_rmse").to_csv(RESULTS_PATH, index=False, encoding="utf-8")
    print(pd.DataFrame(results).sort_values("loso_rmse").to_string(index=False))
    name, pfn, pca_n, params = best_cfg
    Xp_all = pfn(X); Xp_test = pfn(X_test)
    pca = PCA(n_components=pca_n, random_state=42); Xtr = pca.fit_transform(Xp_all); Xtest = pca.transform(Xp_test)
    sc = StandardScaler(); Xtr = sc.fit_transform(Xtr); Xtest = sc.transform(Xtest)
    m = KernelRidge(**params); m.fit(Xtr, y); preds = m.predict(Xtest)
    print(f"\nbest={name} loso={best_rmse:.6f} min={preds.min():.4f} max={preds.max():.4f}")
    if np.any(preds < 0): print(f"negatives={np.sum(preds<0)}, submission_skipped=True"); return
    save_submission(sample_submit_df, test_df, sample_col, preds, SUBMISSIONS_DIR/f"expA039_kr_{name}_submission.csv")
    print(f"saved_submission=expA039_kr_{name}_submission.csv")

if __name__ == "__main__": main()
