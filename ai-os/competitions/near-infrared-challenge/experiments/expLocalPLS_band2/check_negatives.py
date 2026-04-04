from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from train import (
    BAND2_RANGE,
    RESULTS_PATH,
    SUBMISSIONS_DIR,
    apply_preprocessing,
    load_data,
    predict_local_pls,
    save_submission,
    select_band_columns,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

EXPERIMENT_DIR = Path(__file__).resolve().parent
TOP_N = 20


def load_top_results(results_path: Path, top_n: int) -> pd.DataFrame:
    results_df = pd.read_csv(results_path, encoding="utf-8")
    required_cols = {"preproc", "k", "n_comp", "loso_rmse"}
    missing_cols = required_cols - set(results_df.columns)
    if missing_cols:
        raise ValueError(f"results.csv is missing columns: {sorted(missing_cols)}")

    sorted_df = results_df.sort_values("loso_rmse", kind="stable").head(top_n).reset_index(drop=True)
    return sorted_df


def main() -> None:
    train_df, test_df, sample_submit_df, wave_cols, sample_col, _, target_col = load_data()
    band2_cols = select_band_columns(wave_cols, BAND2_RANGE)

    X_train = train_df[band2_cols].to_numpy(dtype=np.float64)
    y_train = train_df[target_col].to_numpy(dtype=np.float64)
    X_test = test_df[band2_cols].to_numpy(dtype=np.float64)

    top_results = load_top_results(RESULTS_PATH, TOP_N)

    print(f"results_path={RESULTS_PATH}")
    print(f"top_n={len(top_results)}")
    print(f"band2_feature_count={len(band2_cols)}")
    print("")

    best_submission_path: Path | None = None

    for _, row in top_results.iterrows():
        preproc = str(row["preproc"])
        k = int(row["k"])
        n_comp = int(row["n_comp"])
        loso_rmse = float(row["loso_rmse"])

        X_train_proc = apply_preprocessing(X_train, preproc)
        X_test_proc = apply_preprocessing(X_test, preproc)
        preds = predict_local_pls(
            X_train=X_train_proc,
            y_train=y_train,
            X_query=X_test_proc,
            k=k,
            n_comp=n_comp,
        )

        has_negative = bool(np.any(preds < 0))
        pred_min = float(preds.min())

        print(
            f"preproc={preproc}, "
            f"k={k}, "
            f"n_comp={n_comp}, "
            f"loso_rmse={loso_rmse:.6f}, "
            f"has_negative={has_negative}, "
            f"pred_min={pred_min:.6f}"
        )

        if has_negative:
            continue

        best_submission_path = SUBMISSIONS_DIR / (
            f"expLocalPLS_band2_{preproc}_k{k}_n{n_comp}_submission.csv"
        )
        save_submission(sample_submit_df, test_df, sample_col, preds, best_submission_path)
        print("")
        print(f"saved_submission={best_submission_path}")
        break

    if best_submission_path is None:
        raise RuntimeError("No non-negative configuration found within the top results.")


if __name__ == "__main__":
    main()
