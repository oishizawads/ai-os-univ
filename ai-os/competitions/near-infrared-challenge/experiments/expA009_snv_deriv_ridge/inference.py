import pickle
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.expA009_snv_deriv_ridge.settings import (
    ID_COL,
    MODEL_PATH,
    SAMPLE_SUBMIT_PATH,
    SUBMISSION_PATH,
    TARGET_COL,
    apply_snv_deriv,
    load_test_df,
)


def main() -> None:
    test_df = load_test_df()

    with MODEL_PATH.open("rb") as fp:
        payload = pickle.load(fp)

    model = payload["model"]
    feature_cols = payload["feature_cols"]
    x_test = test_df[feature_cols].to_numpy(dtype=float)
    x_test = apply_snv_deriv(x_test)
    test_df[TARGET_COL] = model.predict(x_test)

    submission_df = pd.read_csv(
        SAMPLE_SUBMIT_PATH,
        header=None,
        names=[ID_COL, TARGET_COL],
        encoding="cp932",
    )
    pred_df = test_df[[ID_COL, TARGET_COL]].copy()
    submission_df = submission_df[[ID_COL]].merge(
        pred_df, on=ID_COL, how="left", validate="one_to_one"
    )

    if submission_df[TARGET_COL].isna().any():
        missing_ids = submission_df.loc[submission_df[TARGET_COL].isna(), ID_COL].tolist()
        raise ValueError(f"Missing predictions for sample_number values: {missing_ids}")

    SUBMISSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    submission_df.to_csv(SUBMISSION_PATH, index=False, header=False)

    print(f"loaded_model={MODEL_PATH}")
    print(f"test_rows={len(test_df)}")
    print(f"submission_rows={len(submission_df)}")
    print(f"saved_submission={SUBMISSION_PATH}")


if __name__ == "__main__":
    main()
