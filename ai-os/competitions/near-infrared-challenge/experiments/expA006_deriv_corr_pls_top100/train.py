import pickle
import sys
from pathlib import Path

import numpy as np
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GroupKFold

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.expA006_deriv_corr_pls_top100.settings import (
    EXPERIMENT_ID,
    GROUP_COL,
    ID_COL,
    MODEL_NAME,
    MODEL_PATH,
    N_COMPONENTS_CANDIDATES,
    N_FOLDS,
    N_TOP_FEATURES_CANDIDATES,
    OOF_PATH,
    PREPROCESSING,
    SEED,
    TARGET_COL,
    VALIDATION,
    apply_deriv,
    load_test_df,
    load_train_df,
    select_top_features,
    wave_columns,
)


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def evaluate_candidate(
    x: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    n_top: int,
    n_components: int,
) -> tuple[float, np.ndarray, list[float]]:
    splitter = GroupKFold(n_splits=N_FOLDS)
    oof_pred = np.zeros(len(y), dtype=np.float64)
    fold_scores: list[float] = []

    for train_idx, valid_idx in splitter.split(x, y, groups=groups):
        top_idx = select_top_features(x[train_idx], y[train_idx], n_top)
        x_tr = x[train_idx][:, top_idx]
        x_val = x[valid_idx][:, top_idx]

        model = PLSRegression(n_components=n_components, max_iter=500)
        model.fit(x_tr, y[train_idx])
        oof_pred[valid_idx] = model.predict(x_val).ravel()
        fold_scores.append(rmse(y[valid_idx], oof_pred[valid_idx]))

    return rmse(y, oof_pred), oof_pred, fold_scores


def main() -> None:
    train_df = load_train_df()
    test_df = load_test_df()
    feature_cols = wave_columns()

    x_train_raw = train_df[feature_cols].to_numpy(dtype=np.float64)
    y_train = train_df[TARGET_COL].to_numpy(dtype=np.float64)
    groups = train_df[GROUP_COL].to_numpy()
    x_test_raw = test_df[feature_cols].to_numpy(dtype=np.float64)

    x_train = apply_deriv(x_train_raw)
    x_test = apply_deriv(x_test_raw)

    print(f"experiment_id={EXPERIMENT_ID}")
    print(f"validation={VALIDATION}")
    print(f"model={MODEL_NAME}")
    print(f"preprocessing={PREPROCESSING}")
    print(
        f"n_samples={len(train_df)} n_features={x_train.shape[1]} "
        f"n_groups={train_df[GROUP_COL].nunique()} test_rows={len(test_df)}"
    )
    print("")
    print("Sweep results:")
    print(
        f"{'n_top':>8}  {'n_comp':>6}  {'oof_rmse':>10}  "
        f"{'fold_mean':>10}  {'fold_std':>9}"
    )

    sweep_results: list[dict] = []
    best_score = float("inf")
    best_n_top = -1
    best_n_components = -1
    best_oof_pred: np.ndarray | None = None

    for n_top in N_TOP_FEATURES_CANDIDATES:
        for n_components in N_COMPONENTS_CANDIDATES:
            if n_components > n_top:
                continue

            oof_rmse, oof_pred, fold_scores = evaluate_candidate(
                x_train, y_train, groups, n_top, n_components
            )
            fold_mean = float(np.mean(fold_scores))
            fold_std = float(np.std(fold_scores))

            sweep_results.append(
                {
                    "n_top_features": n_top,
                    "n_components": n_components,
                    "oof_rmse": oof_rmse,
                    "fold_rmse_mean": fold_mean,
                    "fold_rmse_std": fold_std,
                }
            )

            print(
                f"{n_top:8d}  {n_components:6d}  {oof_rmse:10.6f}  "
                f"{fold_mean:10.6f}  {fold_std:9.6f}"
            )

            if oof_rmse < best_score:
                best_score = oof_rmse
                best_n_top = n_top
                best_n_components = n_components
                best_oof_pred = oof_pred.copy()

    if best_oof_pred is None:
        raise RuntimeError("No sweep results were produced.")

    print("")
    print(f"best_n_top_features={best_n_top}")
    print(f"best_n_components={best_n_components}")
    print(f"best_oof_rmse={best_score:.6f}")

    selected_idx = select_top_features(x_train, y_train, best_n_top)
    final_model = PLSRegression(n_components=best_n_components, max_iter=500)
    final_model.fit(x_train[:, selected_idx], y_train)

    payload = {
        "experiment_id": EXPERIMENT_ID,
        "seed": SEED,
        "feature_cols": feature_cols,
        "preprocessing": PREPROCESSING,
        "best_n_top_features": best_n_top,
        "best_n_components": best_n_components,
        "selected_feature_indices": selected_idx,
        "sweep_results": sweep_results,
        "model": final_model,
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MODEL_PATH.open("wb") as fp:
        pickle.dump(payload, fp)

    oof_df = train_df[[ID_COL, GROUP_COL, TARGET_COL]].copy()
    oof_df["oof_pred"] = best_oof_pred
    oof_df.to_csv(OOF_PATH, index=False)

    print(f"saved_model={MODEL_PATH}")
    print(f"saved_oof={OOF_PATH}")
    print(f"prepared_test_matrix_shape={x_test[:, selected_idx].shape}")


if __name__ == "__main__":
    main()
