"""
expA053_optuna_all — Multi-model Optuna HPO on band2 (4800-5350 cm-1).
CV: Leave-One-Species-Out (LOSO).  Objective: RMSE (predictions clipped >= 0).
Models: LightGBM, XGBoost, CatBoost, HistGBM, Ridge, ElasticNet,
        SVR, KernelRidge, RandomForest, ExtraTrees, PLS
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import optuna
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut

from _base_band2 import (
    load_data, select_band2, apply_snv, apply_snv_sg1,
    save_submission, SUBMISSIONS_DIR,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
optuna.logging.set_verbosity(optuna.logging.WARNING)

EXPERIMENT_DIR = Path(__file__).resolve().parent
RESULTS_PATH    = EXPERIMENT_DIR / "results.csv"
BEST_PARAMS_DIR = EXPERIMENT_DIR / "best_params"
TRIALS_DIR      = EXPERIMENT_DIR / "trials"

# n_trials per model
N_TRIALS: dict[str, int] = {
    "lgbm":        80,
    "xgb":         80,
    "catboost":    80,
    "histgbm":     80,
    "ridge":       100,
    "elasticnet":  100,
    "svr":         50,
    "kernelridge": 50,
    "rf":          60,
    "et":          60,
    "pls":         50,
}

SEED = 42


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

class _PLSWrapper:
    """Sklearn-compatible wrapper for PLSRegression (predict returns 1-D)."""
    def __init__(self, n_components: int):
        self.n_components = n_components

    def fit(self, X, y):
        from sklearn.cross_decomposition import PLSRegression
        self._m = PLSRegression(n_components=self.n_components, max_iter=500)
        self._m.fit(X, y)
        return self

    def predict(self, X):
        return self._m.predict(X).ravel()


def _loso_rmse(make_model, X: np.ndarray, y: np.ndarray, groups: np.ndarray) -> float:
    logo = LeaveOneGroupOut()
    oof = np.zeros_like(y, dtype=np.float64)
    for tr, val in logo.split(X, y, groups):
        m = make_model()
        m.fit(X[tr], y[tr])
        oof[val] = m.predict(X[val])
    return float(np.sqrt(mean_squared_error(y, np.clip(oof, 0, None))))


# ---------------------------------------------------------------------------
# Objective factories
# ---------------------------------------------------------------------------

def _obj_lgbm(X, y, groups):
    from lightgbm import LGBMRegressor
    def objective(trial: optuna.Trial) -> float:
        p = dict(
            objective="regression", metric="rmse", verbose=-1,
            n_jobs=-1, random_state=SEED,
            n_estimators     = trial.suggest_int  ("n_estimators",     200, 1000, step=100),
            learning_rate    = trial.suggest_float("learning_rate",    0.01, 0.3, log=True),
            num_leaves       = trial.suggest_int  ("num_leaves",       15, 127),
            max_depth        = trial.suggest_int  ("max_depth",        3, 10),
            min_child_samples= trial.suggest_int  ("min_child_samples",5, 50),
            subsample        = trial.suggest_float("subsample",        0.5, 1.0),
            subsample_freq   = 1,
            colsample_bytree = trial.suggest_float("colsample_bytree", 0.4, 1.0),
            reg_alpha        = trial.suggest_float("reg_alpha",        1e-4, 10.0, log=True),
            reg_lambda       = trial.suggest_float("reg_lambda",       1e-4, 10.0, log=True),
        )
        return _loso_rmse(lambda: LGBMRegressor(**p), X, y, groups)
    return objective


def _obj_xgb(X, y, groups):
    from xgboost import XGBRegressor
    def objective(trial: optuna.Trial) -> float:
        p = dict(
            objective="reg:squarederror", verbosity=0,
            random_state=SEED, n_jobs=-1, tree_method="hist",
            n_estimators    = trial.suggest_int  ("n_estimators",    200, 1000, step=100),
            learning_rate   = trial.suggest_float("learning_rate",   0.01, 0.3,  log=True),
            max_depth       = trial.suggest_int  ("max_depth",       3, 10),
            min_child_weight= trial.suggest_int  ("min_child_weight",1, 20),
            subsample       = trial.suggest_float("subsample",       0.5, 1.0),
            colsample_bytree= trial.suggest_float("colsample_bytree",0.4, 1.0),
            gamma           = trial.suggest_float("gamma",           0.0, 5.0),
            reg_alpha       = trial.suggest_float("reg_alpha",       1e-4, 10.0, log=True),
            reg_lambda      = trial.suggest_float("reg_lambda",      1e-4, 10.0, log=True),
        )
        return _loso_rmse(lambda: XGBRegressor(**p), X, y, groups)
    return objective


def _obj_catboost(X, y, groups, train_dir: str):
    from catboost import CatBoostRegressor
    def objective(trial: optuna.Trial) -> float:
        p = dict(
            loss_function="RMSE", verbose=0, random_seed=SEED,
            train_dir=train_dir,
            iterations        = trial.suggest_int  ("iterations",         200, 1000, step=100),
            learning_rate     = trial.suggest_float("learning_rate",      0.01, 0.3,  log=True),
            depth             = trial.suggest_int  ("depth",              3, 10),
            l2_leaf_reg       = trial.suggest_float("l2_leaf_reg",        1e-4, 10.0, log=True),
            bagging_temperature= trial.suggest_float("bagging_temperature",0.0, 1.0),
            random_strength   = trial.suggest_float("random_strength",    0.0, 10.0),
        )
        return _loso_rmse(lambda: CatBoostRegressor(**p), X, y, groups)
    return objective


def _obj_histgbm(X, y, groups):
    from sklearn.ensemble import HistGradientBoostingRegressor
    def objective(trial: optuna.Trial) -> float:
        p = dict(
            random_state=SEED,
            max_iter         = trial.suggest_int  ("max_iter",          200, 1000, step=100),
            learning_rate    = trial.suggest_float("learning_rate",     0.01, 0.2,  log=True),
            max_leaf_nodes   = trial.suggest_int  ("max_leaf_nodes",    15, 127),
            max_depth        = trial.suggest_int  ("max_depth",         3, 10),
            min_samples_leaf = trial.suggest_int  ("min_samples_leaf",  5, 50),
            l2_regularization= trial.suggest_float("l2_regularization", 1e-4, 10.0, log=True),
        )
        return _loso_rmse(lambda: HistGradientBoostingRegressor(**p), X, y, groups)
    return objective


def _obj_ridge(X, y, groups):
    from sklearn.linear_model import Ridge
    def objective(trial: optuna.Trial) -> float:
        alpha = trial.suggest_float("alpha", 1e-3, 1e4, log=True)
        return _loso_rmse(lambda: Ridge(alpha=alpha), X, y, groups)
    return objective


def _obj_elasticnet(X, y, groups):
    from sklearn.linear_model import ElasticNet
    def objective(trial: optuna.Trial) -> float:
        alpha    = trial.suggest_float("alpha",    1e-3, 10.0, log=True)
        l1_ratio = trial.suggest_float("l1_ratio", 0.0, 1.0)
        return _loso_rmse(
            lambda: ElasticNet(alpha=alpha, l1_ratio=l1_ratio,
                               max_iter=5000, random_state=SEED),
            X, y, groups,
        )
    return objective


def _obj_svr(X, y, groups):
    from sklearn.svm import SVR
    def objective(trial: optuna.Trial) -> float:
        C       = trial.suggest_float("C",       1e-1, 1e4,  log=True)
        gamma   = trial.suggest_float("gamma",   1e-4, 10.0, log=True)
        epsilon = trial.suggest_float("epsilon", 1e-3, 1.0,  log=True)
        return _loso_rmse(lambda: SVR(kernel="rbf", C=C, gamma=gamma, epsilon=epsilon), X, y, groups)
    return objective


def _obj_kernelridge(X, y, groups):
    from sklearn.kernel_ridge import KernelRidge
    def objective(trial: optuna.Trial) -> float:
        alpha = trial.suggest_float("alpha", 1e-4, 10.0, log=True)
        gamma = trial.suggest_float("gamma", 1e-4, 10.0, log=True)
        return _loso_rmse(lambda: KernelRidge(kernel="rbf", alpha=alpha, gamma=gamma), X, y, groups)
    return objective


def _obj_rf(X, y, groups):
    from sklearn.ensemble import RandomForestRegressor
    def objective(trial: optuna.Trial) -> float:
        p = dict(
            n_jobs=-1, random_state=SEED,
            n_estimators    = trial.suggest_int  ("n_estimators",    100, 500, step=50),
            max_depth       = trial.suggest_int  ("max_depth",       3, 20),
            min_samples_split= trial.suggest_int ("min_samples_split",2, 20),
            min_samples_leaf= trial.suggest_int  ("min_samples_leaf", 1, 20),
            max_features    = trial.suggest_float("max_features",     0.3, 1.0),
        )
        return _loso_rmse(lambda: RandomForestRegressor(**p), X, y, groups)
    return objective


def _obj_et(X, y, groups):
    from sklearn.ensemble import ExtraTreesRegressor
    def objective(trial: optuna.Trial) -> float:
        p = dict(
            n_jobs=-1, random_state=SEED,
            n_estimators    = trial.suggest_int  ("n_estimators",    100, 500, step=50),
            max_depth       = trial.suggest_int  ("max_depth",       3, 20),
            min_samples_split= trial.suggest_int ("min_samples_split",2, 20),
            min_samples_leaf= trial.suggest_int  ("min_samples_leaf", 1, 20),
            max_features    = trial.suggest_float("max_features",     0.3, 1.0),
        )
        return _loso_rmse(lambda: ExtraTreesRegressor(**p), X, y, groups)
    return objective


def _obj_pls(X, y, groups):
    max_comp = min(20, X.shape[1], X.shape[0] - 1)
    def objective(trial: optuna.Trial) -> float:
        n_components = trial.suggest_int("n_components", 1, max_comp)
        return _loso_rmse(lambda: _PLSWrapper(n_components), X, y, groups)
    return objective


# ---------------------------------------------------------------------------
# Model builder (for final full-train prediction)
# ---------------------------------------------------------------------------

def _build_model(model_name: str, params: dict, catboost_train_dir: str | None = None):
    if model_name == "lgbm":
        from lightgbm import LGBMRegressor
        return LGBMRegressor(**params)
    if model_name == "xgb":
        from xgboost import XGBRegressor
        return XGBRegressor(**params)
    if model_name == "catboost":
        from catboost import CatBoostRegressor
        return CatBoostRegressor(**params, train_dir=catboost_train_dir)
    if model_name == "histgbm":
        from sklearn.ensemble import HistGradientBoostingRegressor
        return HistGradientBoostingRegressor(**params)
    if model_name == "ridge":
        from sklearn.linear_model import Ridge
        return Ridge(**params)
    if model_name == "elasticnet":
        from sklearn.linear_model import ElasticNet
        return ElasticNet(**params, max_iter=5000, random_state=SEED)
    if model_name == "svr":
        from sklearn.svm import SVR
        return SVR(kernel="rbf", **params)
    if model_name == "kernelridge":
        from sklearn.kernel_ridge import KernelRidge
        return KernelRidge(kernel="rbf", **params)
    if model_name == "rf":
        from sklearn.ensemble import RandomForestRegressor
        return RandomForestRegressor(**params, n_jobs=-1)
    if model_name == "et":
        from sklearn.ensemble import ExtraTreesRegressor
        return ExtraTreesRegressor(**params, n_jobs=-1)
    if model_name == "pls":
        return _PLSWrapper(**params)
    raise ValueError(f"Unknown model: {model_name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    BEST_PARAMS_DIR.mkdir(parents=True, exist_ok=True)
    TRIALS_DIR.mkdir(parents=True, exist_ok=True)
    SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)
    CB_TRAIN_DIR = str(EXPERIMENT_DIR / "catboost_info")

    train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col = load_data()
    band2_cols = select_band2(wave_cols)
    X_raw      = train_df[band2_cols].to_numpy(dtype=np.float64)
    y          = train_df[target_col].to_numpy(dtype=np.float64)
    groups     = train_df[species_col].to_numpy()
    X_test_raw = test_df[band2_cols].to_numpy(dtype=np.float64)

    n_species = len(np.unique(groups))
    print(f"band2_features={len(band2_cols)}  n_train={len(y)}  n_species={n_species}")

    OBJECTIVE_FACTORIES = {
        "lgbm":        _obj_lgbm,
        "xgb":         _obj_xgb,
        "histgbm":     _obj_histgbm,
        "ridge":       _obj_ridge,
        "elasticnet":  _obj_elasticnet,
        "svr":         _obj_svr,
        "kernelridge": _obj_kernelridge,
        "rf":          _obj_rf,
        "et":          _obj_et,
        "pls":         _obj_pls,
    }

    preprocs = [("snv", apply_snv), ("snv_sg1", apply_snv_sg1)]
    results  = []

    all_models = list(OBJECTIVE_FACTORIES.keys()) + ["catboost"]

    for model_name in all_models:
        for preproc_name, preproc_fn in preprocs:
            # Resume: skip if already done
            trials_csv = TRIALS_DIR / f"{model_name}_{preproc_name}.csv"
            params_json = BEST_PARAMS_DIR / f"{model_name}_{preproc_name}.json"
            if trials_csv.exists() and params_json.exists():
                print(f"\n[SKIP] model={model_name}  preproc={preproc_name}  (already done)")
                # Load previous best for results list
                with open(params_json, encoding="utf-8") as f:
                    prev_params = json.load(f)
                prev_trials = pd.read_csv(trials_csv)
                best_val = prev_trials["value"].min() if "value" in prev_trials.columns else float("nan")
                results.append({"model": model_name, "preproc": preproc_name, "loso_rmse": best_val})
                continue

            X      = preproc_fn(X_raw)
            X_test = preproc_fn(X_test_raw)
            n_trials = N_TRIALS.get(model_name, 50)

            print(f"\n[Optuna] model={model_name:<12}  preproc={preproc_name:<8}  n_trials={n_trials}")

            if model_name == "catboost":
                objective = _obj_catboost(X, y, groups, CB_TRAIN_DIR)
            else:
                objective = OBJECTIVE_FACTORIES[model_name](X, y, groups)

            study = optuna.create_study(
                direction="minimize",
                sampler=optuna.samplers.TPESampler(seed=SEED),
            )
            study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

            best  = study.best_trial
            print(f"  best_loso={best.value:.6f}")
            print(f"  best_params={best.params}")

            # --- save trial history ---
            study.trials_dataframe().to_csv(
                TRIALS_DIR / f"{model_name}_{preproc_name}.csv",
                index=False, encoding="utf-8",
            )

            # --- save best params ---
            with open(BEST_PARAMS_DIR / f"{model_name}_{preproc_name}.json", "w", encoding="utf-8") as f:
                json.dump(best.params, f, indent=2)

            # --- full-train prediction & submission ---
            if model_name == "catboost":
                full_params = dict(
                    loss_function="RMSE", verbose=0, random_seed=SEED,
                    train_dir=CB_TRAIN_DIR, **best.params,
                )
            elif model_name == "lgbm":
                full_params = dict(
                    objective="regression", metric="rmse", verbose=-1,
                    n_jobs=-1, random_state=SEED, subsample_freq=1, **best.params,
                )
            elif model_name == "xgb":
                full_params = dict(
                    objective="reg:squarederror", verbosity=0,
                    random_state=SEED, n_jobs=-1, tree_method="hist", **best.params,
                )
            else:
                full_params = dict(random_state=SEED, **best.params) if model_name in ("histgbm", "rf", "et") else best.params.copy()

            model = _build_model(model_name, full_params, catboost_train_dir=CB_TRAIN_DIR)
            model.fit(X, y)
            preds = np.clip(model.predict(X_test), 0, None)
            sub_path = SUBMISSIONS_DIR / f"expA053_{model_name}_{preproc_name}_submission.csv"
            save_submission(sample_submit_df, test_df, sample_col, preds, sub_path)
            print(f"  saved_submission={sub_path.name}")

            results.append({
                "model":     model_name,
                "preproc":   preproc_name,
                "loso_rmse": best.value,
            })

    # --- save consolidated results ---
    results_df = pd.DataFrame(results).sort_values("loso_rmse").reset_index(drop=True)
    results_df.to_csv(RESULTS_PATH, index=False, encoding="utf-8")
    print("\n=== Final Results ===")
    print(results_df.to_string(index=False))
    print(f"\nsaved={RESULTS_PATH}")


if __name__ == "__main__":
    main()
