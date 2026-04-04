import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.expA002_kfold_baseline.settings import (
    ALPHA,
    EXPERIMENT_ID,
    ID_COL,
    MODEL_NAME,
    MODEL_PATH,
    N_FOLDS,
    OOF_PATH,
    SEED,
    TARGET_COL,
    VALIDATION,
    load_train_df,
    wave_columns,
)


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def main() -> None:
    train_df = load_train_df()
    feature_cols = wave_columns()

    x = train_df[feature_cols].to_numpy(dtype=np.float64)
    y = train_df[TARGET_COL].to_numpy(dtype=np.float64)

    splitter = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    oof_pred = np.zeros(len(train_df), dtype=np.float64)
    fold_scores: list[float] = []

    print(f"experiment_id={EXPERIMENT_ID}")
    print(f"validation={VALIDATION}")
    print(f"model={MODEL_NAME}(alpha={ALPHA})")
    print(f"n_samples={len(train_df)} n_features={len(feature_cols)}")

    for fold, (train_idx, valid_idx) in enumerate(splitter.split(x, y), start=1):
        model = Ridge(alpha=ALPHA)
        model.fit(x[train_idx], y[train_idx])
        valid_pred = model.predict(x[valid_idx])
        fold_rmse = rmse(y[valid_idx], valid_pred)

        oof_pred[valid_idx] = valid_pred
        fold_scores.append(fold_rmse)

        print(
            f"fold={fold} rmse={fold_rmse:.6f} "
            f"train_size={len(train_idx)} valid_size={len(valid_idx)}"
        )

    overall_rmse = rmse(y, oof_pred)
    print(f"cv_rmse_mean={np.mean(fold_scores):.6f}")
    print(f"cv_rmse_std={np.std(fold_scores):.6f}")
    print(f"cv_rmse_oof={overall_rmse:.6f}")

    final_model = Ridge(alpha=ALPHA)
    final_model.fit(x, y)

    payload = {
        "experiment_id": EXPERIMENT_ID,
        "seed": SEED,
        "feature_cols": feature_cols,
        "model": final_model,
    }
    with MODEL_PATH.open("wb") as fp:
        pickle.dump(payload, fp)

    oof_df = train_df[[ID_COL, TARGET_COL]].copy()
    oof_df["oof_pred"] = oof_pred
    oof_df.to_csv(OOF_PATH, index=False)

    print(f"saved_model={MODEL_PATH}")
    print(f"saved_oof={OOF_PATH}")


if __name__ == "__main__":
    main()
