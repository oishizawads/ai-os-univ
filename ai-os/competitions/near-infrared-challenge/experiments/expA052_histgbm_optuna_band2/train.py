"""HistGradientBoostingRegressor + Optuna hyperparameter tuning on band2."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import optuna
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut
from _base_band2 import load_data, select_band2, apply_snv, apply_snv_sg1, save_submission, SUBMISSIONS_DIR

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
optuna.logging.set_verbosity(optuna.logging.WARNING)

EXPERIMENT_DIR = Path(__file__).resolve().parent
RESULTS_PATH = EXPERIMENT_DIR / "results.csv"
N_TRIALS = 100


def loso_rmse(params, X, y, groups):
    logo = LeaveOneGroupOut()
    oof = np.zeros_like(y, dtype=np.float64)
    for tr, val in logo.split(X, y, groups):
        m = HistGradientBoostingRegressor(**params); m.fit(X[tr], y[tr]); oof[val] = m.predict(X[val])
    return float(np.sqrt(mean_squared_error(y, np.clip(oof, 0, None))))


def make_objective(X, y, groups):
    def objective(trial):
        params = {
            "random_state":      42,
            "max_iter":          trial.suggest_int("max_iter", 200, 1000, step=100),
            "learning_rate":     trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            "max_leaf_nodes":    trial.suggest_int("max_leaf_nodes", 15, 127),
            "max_depth":         trial.suggest_int("max_depth", 3, 10),
            "min_samples_leaf":  trial.suggest_int("min_samples_leaf", 5, 50),
            "l2_regularization": trial.suggest_float("l2_regularization", 1e-4, 10.0, log=True),
            "max_bins":          trial.suggest_int("max_bins", 64, 255),
        }
        return loso_rmse(params, X, y, groups)
    return objective


def main():
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
    train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col = load_data()
    band2_cols = select_band2(wave_cols)
    X_raw = train_df[band2_cols].to_numpy(dtype=np.float64)
    y = train_df[target_col].to_numpy(dtype=np.float64)
    groups = train_df[species_col].to_numpy()
    X_test_raw = test_df[band2_cols].to_numpy(dtype=np.float64)
    print(f"band2_features={len(band2_cols)}")

    results = []
    for preproc_name, preproc_fn in [("snv", apply_snv), ("snv_sg1", apply_snv_sg1)]:
        X = preproc_fn(X_raw); X_test = preproc_fn(X_test_raw)
        print(f"\n[Optuna HistGBM] preproc={preproc_name} n_trials={N_TRIALS}")
        study = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=42))
        study.optimize(make_objective(X, y, groups), n_trials=N_TRIALS)
        best_params = {**study.best_trial.params}
        best_loso = loso_rmse(best_params, X, y, groups)
        print(f"  best_loso={best_loso:.6f}  params={study.best_trial.params}")
        results.append({"preproc": preproc_name, "loso_rmse": best_loso, **study.best_trial.params})
        m = HistGradientBoostingRegressor(**best_params); m.fit(X, y)
        preds = np.clip(m.predict(X_test), 0, None)
        save_submission(sample_submit_df, test_df, sample_col, preds,
                        SUBMISSIONS_DIR / f"expA052_histgbm_optuna_{preproc_name}_submission.csv")
        print(f"  saved_submission=expA052_histgbm_optuna_{preproc_name}_submission.csv")
        study.trials_dataframe().to_csv(EXPERIMENT_DIR / f"trials_{preproc_name}.csv", index=False, encoding="utf-8")

    pd.DataFrame(results).sort_values("loso_rmse").to_csv(RESULTS_PATH, index=False, encoding="utf-8")
    print("\n=== Results ===")
    print(pd.DataFrame(results)[["preproc","loso_rmse"]].to_string(index=False))

if __name__ == "__main__": main()
