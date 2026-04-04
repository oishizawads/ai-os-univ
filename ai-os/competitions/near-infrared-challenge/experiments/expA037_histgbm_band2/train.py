from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut
from _base_band2 import load_data, select_band2, apply_snv, apply_snv_sg1, save_submission, SUBMISSIONS_DIR

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

EXPERIMENT_DIR = Path(__file__).resolve().parent
RESULTS_PATH = EXPERIMENT_DIR / "results.csv"

SETTINGS = [
    ("snv_histgbm",       apply_snv,     {"max_iter": 500, "learning_rate": 0.05, "max_leaf_nodes": 31, "min_samples_leaf": 20, "random_state": 42}),
    ("snv_sg1_histgbm",   apply_snv_sg1, {"max_iter": 500, "learning_rate": 0.05, "max_leaf_nodes": 31, "min_samples_leaf": 20, "random_state": 42}),
    ("snv_histgbm_deep",  apply_snv,     {"max_iter": 500, "learning_rate": 0.05, "max_leaf_nodes": 63, "min_samples_leaf": 10, "random_state": 42}),
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
    best_rmse, best_name, best_preproc_fn, best_params = float("inf"), None, None, None

    for name, preproc_fn, params in SETTINGS:
        Xp = preproc_fn(X)
        oof = np.zeros_like(y, dtype=np.float64)
        for fold, (tr, val) in enumerate(logo.split(Xp, y, groups), 1):
            m = HistGradientBoostingRegressor(**params)
            m.fit(Xp[tr], y[tr])
            oof[val] = m.predict(Xp[val])
            print(f"  [{name}] fold={fold} holdout={np.unique(groups[val]).tolist()} rmse={np.sqrt(mean_squared_error(y[val], oof[val])):.4f}")
        rmse = float(np.sqrt(mean_squared_error(y, oof)))
        results.append({"setting": name, "loso_rmse": rmse})
        print(f"[{name}] LOSO={rmse:.6f}\n")
        if rmse < best_rmse:
            best_rmse, best_name, best_preproc_fn, best_params = rmse, name, preproc_fn, params

    pd.DataFrame(results).sort_values("loso_rmse").to_csv(RESULTS_PATH, index=False, encoding="utf-8")
    print(pd.DataFrame(results).sort_values("loso_rmse").to_string(index=False))

    Xp_all = best_preproc_fn(X)
    Xp_test = best_preproc_fn(X_test)
    m = HistGradientBoostingRegressor(**best_params)
    m.fit(Xp_all, y)
    preds = m.predict(Xp_test)
    print(f"\nbest={best_name} loso={best_rmse:.6f} pred_min={preds.min():.4f} pred_max={preds.max():.4f}")
    if np.any(preds < 0):
        print(f"negatives={np.sum(preds<0)}, submission_skipped=True"); return
    save_submission(sample_submit_df, test_df, sample_col, preds, SUBMISSIONS_DIR / f"expA037_histgbm_{best_name}_submission.csv")
    print(f"saved_submission=expA037_histgbm_{best_name}_submission.csv")

if __name__ == "__main__":
    main()
