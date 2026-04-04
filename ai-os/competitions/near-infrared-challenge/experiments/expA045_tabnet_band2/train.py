from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from pytorch_tabnet.tab_model import TabNetRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler
from _base_band2 import load_data, select_band2, apply_snv, apply_snv_sg1, save_submission, SUBMISSIONS_DIR
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")

EXPERIMENT_DIR = Path(__file__).resolve().parent
RESULTS_PATH = EXPERIMENT_DIR / "results.csv"

TABNET_PARAMS = {
    "n_d": 32, "n_a": 32, "n_steps": 5,
    "gamma": 1.3, "momentum": 0.02,
    "optimizer_fn": __import__("torch").optim.Adam,
    "optimizer_params": {"lr": 2e-3, "weight_decay": 1e-5},
    "scheduler_fn": __import__("torch").optim.lr_scheduler.StepLR,
    "scheduler_params": {"step_size": 50, "gamma": 0.9},
    "verbose": 0, "seed": 42,
}
FIT_PARAMS = {"max_epochs": 200, "patience": 20, "batch_size": 256, "virtual_batch_size": 128}

SETTINGS = [("snv_tabnet", apply_snv), ("snv_sg1_tabnet", apply_snv_sg1)]

def main():
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
    train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col = load_data()
    band2_cols = select_band2(wave_cols)
    X = train_df[band2_cols].to_numpy(dtype=np.float64); y = train_df[target_col].to_numpy(dtype=np.float64)
    groups = train_df[species_col].to_numpy(); X_test = test_df[band2_cols].to_numpy(dtype=np.float64)
    logo = LeaveOneGroupOut()
    results = []; best_rmse, best_name, best_pfn = float("inf"), None, None
    for name, pfn in SETTINGS:
        Xp = pfn(X); oof = np.zeros_like(y, dtype=np.float64)
        for fold, (tr, val) in enumerate(logo.split(Xp, y, groups), 1):
            sc = StandardScaler()
            Xtr = sc.fit_transform(Xp[tr]).astype(np.float32); Xval = sc.transform(Xp[val]).astype(np.float32)
            ytr = y[tr].reshape(-1,1).astype(np.float32)
            m = TabNetRegressor(**TABNET_PARAMS)
            m.fit(Xtr, ytr, **FIT_PARAMS)
            oof[val] = m.predict(Xval).ravel()
            print(f"  [{name}] fold={fold} holdout={np.unique(groups[val]).tolist()} rmse={np.sqrt(mean_squared_error(y[val], oof[val])):.4f}")
        rmse = float(np.sqrt(mean_squared_error(y, oof)))
        results.append({"setting": name, "loso_rmse": rmse}); print(f"[{name}] LOSO={rmse:.6f}\n")
        if rmse < best_rmse: best_rmse, best_name, best_pfn = rmse, name, pfn
    pd.DataFrame(results).sort_values("loso_rmse").to_csv(RESULTS_PATH, index=False, encoding="utf-8")
    print(pd.DataFrame(results).sort_values("loso_rmse").to_string(index=False))
    Xp_all = best_pfn(X); Xp_test = best_pfn(X_test)
    sc = StandardScaler(); Xtr = sc.fit_transform(Xp_all).astype(np.float32); Xtest = sc.transform(Xp_test).astype(np.float32)
    m = TabNetRegressor(**TABNET_PARAMS)
    m.fit(Xtr, y.reshape(-1,1).astype(np.float32), **FIT_PARAMS)
    preds = m.predict(Xtest).ravel()
    print(f"\nbest={best_name} loso={best_rmse:.6f} min={preds.min():.4f} max={preds.max():.4f}")
    if np.any(preds < 0): print(f"negatives={np.sum(preds<0)}, submission_skipped=True"); return
    save_submission(sample_submit_df, test_df, sample_col, preds, SUBMISSIONS_DIR/f"expA045_tabnet_{best_name}_submission.csv")
    print(f"saved_submission=expA045_tabnet_{best_name}_submission.csv")

if __name__ == "__main__": main()
