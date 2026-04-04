import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GroupKFold

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.expA004_snv_pls.settings import (
    EXPERIMENT_ID,
    GROUP_COL,
    ID_COL,
    MODEL_NAME,
    MODEL_PATH,
    N_COMPONENTS_CANDIDATES,
    N_FOLDS,
    OOF_PATH,
    PREPROCESSING,
    SEED,
    TARGET_COL,
    VALIDATION,
    apply_snv,
    load_test_df,
    load_train_df,
    wave_columns,
)


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def build_model(n_components: int) -> PLSRegression:
    return PLSRegression(n_components=n_components, max_iter=500)


def evaluate_candidate(
    x: np.ndarray, y: np.ndarray, groups: np.ndarray, n_components: int
) -> tuple[float, np.ndarray, list[float]]:
    splitter = GroupKFold(n_splits=N_FOLDS)
    oof_pred = np.zeros(len(y), dtype=np.float64)
    fold_scores: list[float] = []

    for train_idx, valid_idx in splitter.split(x, y, groups=groups):
        model = build_model(n_components)
        model.fit(x[train_idx], y[train_idx])
        valid_pred = model.predict(x[valid_idx]).ravel()

        oof_pred[valid_idx] = valid_pred
        fold_scores.append(rmse(y[valid_idx], valid_pred))

    return rmse(y, oof_pred), oof_pred, fold_scores


def main() -> None:
    train_df = load_train_df()
    test_df = load_test_df()
    feature_cols = wave_columns()

    x_train = train_df[feature_cols].to_numpy(dtype=np.float64)
    y_train = train_df[TARGET_COL].to_numpy(dtype=np.float64)
    groups = train_df[GROUP_COL].to_numpy()
    x_test = test_df[feature_cols].to_numpy(dtype=np.float64)

    x_train = apply_snv(x_train)
    x_test = apply_snv(x_test)

    print(f"experiment_id={EXPERIMENT_ID}")
    print(f"validation={VALIDATION}")
    print(f"model={MODEL_NAME}")
    print(f"preprocessing={PREPROCESSING}")
    print(
        f"n_samples={len(train_df)} n_features={len(feature_cols)} "
        f"n_groups={train_df[GROUP_COL].nunique()} test_rows={len(test_df)}"
    )
    print("")
    print("Sweep results:")
    print(f"{'n_components':>12}  {'oof_rmse':>10}  {'fold_rmse_mean':>14}  {'fold_rmse_std':>13}")

    sweep_results: list[dict[str, float | int]] = []
    best_score = float("inf")
    best_n_components = -1
    best_oof_pred: np.ndarray | None = None

    for n_components in N_COMPONENTS_CANDIDATES:
        oof_rmse, oof_pred, fold_scores = evaluate_candidate(
            x_train, y_train, groups, n_components
        )
        fold_mean = float(np.mean(fold_scores))
        fold_std = float(np.std(fold_scores))

        sweep_results.append(
            {
                "n_components": n_components,
                "oof_rmse": oof_rmse,
                "fold_rmse_mean": fold_mean,
                "fold_rmse_std": fold_std,
            }
        )

        print(f"{n_components:12d}  {oof_rmse:10.6f}  {fold_mean:14.6f}  {fold_std:13.6f}")

        if oof_rmse < best_score:
            best_score = oof_rmse
            best_n_components = n_components
            best_oof_pred = oof_pred.copy()

    if best_oof_pred is None:
        raise RuntimeError("No sweep results were produced.")

    print("")
    print(f"best_n_components={best_n_components}")
    print(f"best_oof_rmse={best_score:.6f}")

    final_model = build_model(best_n_components)
    final_model.fit(x_train, y_train)

    payload = {
        "experiment_id": EXPERIMENT_ID,
        "seed": SEED,
        "feature_cols": feature_cols,
        "preprocessing": PREPROCESSING,
        "best_n_components": best_n_components,
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
    print(f"prepared_test_matrix_shape={x_test.shape}")


if __name__ == "__main__":
    main()
