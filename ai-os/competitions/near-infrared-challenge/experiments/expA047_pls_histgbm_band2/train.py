"""
2-stage: PLS scores (extracted per fold) → HistGradientBoostingRegressor
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut
from _base_band2 import (
    load_data, select_band2, apply_snv, apply_snv_sg1,
    save_submission, SUBMISSIONS_DIR
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

EXPERIMENT_DIR = Path(__file__).resolve().parent
RESULTS_PATH = EXPERIMENT_DIR / "results.csv"

HISTGBM_PARAMS = {
    "max_iter": 500, "learning_rate": 0.05, "max_leaf_nodes": 31,
    "min_samples_leaf": 20, "random_state": 42,
}

SETTINGS = [
    ("snv_pls10_hgbm",     apply_snv,     10),
    ("snv_pls20_hgbm",     apply_snv,     20),
    ("snv_pls30_hgbm",     apply_snv,     30),
    ("snv_sg1_pls10_hgbm", apply_snv_sg1, 10),
    ("snv_sg1_pls20_hgbm", apply_snv_sg1, 20),
    ("snv_sg1_pls30_hgbm", apply_snv_sg1, 30),
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

    for name, preproc_fn, n_comp in SETTINGS:
        Xp = preproc_fn(X)
        oof = np.zeros_like(y, dtype=np.float64)

        for fold, (tr, val) in enumerate(logo.split(Xp, y, groups), 1):
            # PLS fit on train fold only (no leakage)
            pls = PLSRegression(n_components=n_comp, max_iter=500)
            pls.fit(Xp[tr], y[tr])
            X_tr_scores = pls.transform(Xp[tr])
            X_val_scores = pls.transform(Xp[val])

            hgbm = HistGradientBoostingRegressor(**HISTGBM_PARAMS)
            hgbm.fit(X_tr_scores, y[tr])
            oof[val] = hgbm.predict(X_val_scores)

            fold_rmse = float(np.sqrt(mean_squared_error(y[val], oof[val])))
            print(f"  [{name}] fold={fold} holdout={np.unique(groups[val]).tolist()} rmse={fold_rmse:.4f}")

        rmse = float(np.sqrt(mean_squared_error(y, oof)))
        results.append({"setting": name, "n_pls": n_comp, "loso_rmse": rmse})
        print(f"[{name}] LOSO={rmse:.6f}\n")
        if rmse < best_rmse:
            best_rmse, best_cfg = rmse, (name, preproc_fn, n_comp)

    results_df = pd.DataFrame(results).sort_values("loso_rmse").reset_index(drop=True)
    results_df.to_csv(RESULTS_PATH, index=False, encoding="utf-8")
    print(results_df.to_string(index=False))
    print(f"\nsaved_results={RESULTS_PATH}")

    # Test predictions with best config
    name, preproc_fn, n_comp = best_cfg
    Xp_all = preproc_fn(X)
    Xp_test = preproc_fn(X_test)
    pls_final = PLSRegression(n_components=n_comp, max_iter=500)
    pls_final.fit(Xp_all, y)
    X_tr_scores = pls_final.transform(Xp_all)
    X_test_scores = pls_final.transform(Xp_test)
    hgbm_final = HistGradientBoostingRegressor(**HISTGBM_PARAMS)
    hgbm_final.fit(X_tr_scores, y)
    preds = hgbm_final.predict(X_test_scores)

    print(f"\nbest={name} n_pls={n_comp} loso={best_rmse:.6f}")
    print(f"pred_min={preds.min():.4f} pred_max={preds.max():.4f}")
    if np.any(preds < 0):
        preds = np.clip(preds, 0, None)
        print(f"clipped to 0")
    save_submission(sample_submit_df, test_df, sample_col, preds,
                    SUBMISSIONS_DIR / f"expA047_pls_histgbm_{name}_submission.csv")
    print(f"saved_submission=expA047_pls_histgbm_{name}_submission.csv")


if __name__ == "__main__":
    main()
