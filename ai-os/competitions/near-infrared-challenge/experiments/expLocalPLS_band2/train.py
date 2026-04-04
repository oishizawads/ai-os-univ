from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"
EXPERIMENT_DIR = Path(__file__).resolve().parent
SUBMISSIONS_DIR = PROJECT_ROOT / "submissions"

TRAIN_PATH = DATA_DIR / "train.csv"
TEST_PATH = DATA_DIR / "test.csv"
SAMPLE_SUBMIT_PATH = DATA_DIR / "sample_submit.csv"
RESULTS_PATH = EXPERIMENT_DIR / "results.csv"

TRAIN_ENCODING = "cp932"
TEST_ENCODING = "cp932"
SUBMIT_ENCODING = "cp932"

BAND2_RANGE = (4800.0, 5350.0)
PREPROCESSINGS = ["raw", "snv", "snv_sg1"]
K_VALUES = [30, 50, 100, 200, 400]
N_COMP_VALUES = [3, 5, 8, 10]


def is_float_column(col_name: str) -> bool:
    try:
        float(col_name)
        return True
    except ValueError:
        return False


def pick_column(columns: list[str], candidates: list[str], fallback_index: int | None = None) -> str:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    if fallback_index is not None:
        return columns[fallback_index]
    raise KeyError(f"Column not found. candidates={candidates}")


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str], str, str, str]:
    train_df = pd.read_csv(TRAIN_PATH, encoding=TRAIN_ENCODING)
    test_df = pd.read_csv(TEST_PATH, encoding=TEST_ENCODING)
    sample_submit_df = pd.read_csv(
        SAMPLE_SUBMIT_PATH,
        header=None,
        names=["sample_number", "prediction"],
        encoding=SUBMIT_ENCODING,
    )

    train_columns = train_df.columns.tolist()
    sample_col = pick_column(train_columns, ["sample_number", "sample number"], fallback_index=0)
    species_col = pick_column(train_columns, ["species", "樹種"], fallback_index=2)
    target_col = pick_column(train_columns, ["MC", "含水率"], fallback_index=3)
    wave_cols = [col for col in train_columns if is_float_column(col)]

    if not wave_cols:
        raise ValueError("No wavelength columns detected.")

    return train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col


def select_band_columns(wave_cols: list[str], wn_range: tuple[float, float]) -> list[str]:
    wn = np.array([float(col) for col in wave_cols], dtype=np.float64)
    mask = (wn >= wn_range[0]) & (wn <= wn_range[1])
    selected = [col for col, keep in zip(wave_cols, mask) if keep]
    if not selected:
        raise ValueError(f"No wavelengths found in range {wn_range}.")
    return selected


def apply_preprocessing(X: np.ndarray, method: str) -> np.ndarray:
    X = X.astype(np.float64, copy=True)

    if method == "raw":
        return X

    row_mean = X.mean(axis=1, keepdims=True)
    row_std = np.clip(X.std(axis=1, keepdims=True), 1e-8, None)
    X = (X - row_mean) / row_std

    if method == "snv":
        return X
    if method == "snv_sg1":
        return savgol_filter(X, window_length=11, polyorder=2, deriv=1, axis=1)

    raise ValueError(f"Unknown preprocessing: {method}")


def normalize_rows(X: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.clip(norms, 1e-12, None)


def predict_local_pls(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_query: np.ndarray,
    k: int,
    n_comp: int,
) -> np.ndarray:
    k_eff = min(k, len(X_train))
    X_train_norm = normalize_rows(X_train)
    X_query_norm = normalize_rows(X_query)
    similarities = X_query_norm @ X_train_norm.T
    topk_idx = np.argpartition(-similarities, kth=k_eff - 1, axis=1)[:, :k_eff]

    preds: list[float] = []
    for i, idx in enumerate(topk_idx):
        local_order = np.argsort(-similarities[i, idx])
        idx = idx[local_order]
        X_local = X_train[idx]
        y_local = y_train[idx]
        max_comp = min(n_comp, X_local.shape[0] - 1, X_local.shape[1])
        if max_comp < 1:
            preds.append(float(np.mean(y_local)))
            continue

        model = PLSRegression(n_components=max_comp, max_iter=500)
        model.fit(X_local, y_local)
        pred = model.predict(X_query[i : i + 1]).ravel()[0]
        preds.append(float(pred))

    return np.array(preds, dtype=np.float64)


def run_loso_grid(
    X: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
) -> pd.DataFrame:
    logo = LeaveOneGroupOut()
    results: list[dict[str, float | int | str]] = []
    total = len(PREPROCESSINGS) * len(K_VALUES) * len(N_COMP_VALUES)
    done = 0

    for preproc in PREPROCESSINGS:
        X_proc = apply_preprocessing(X, preproc)
        for k in K_VALUES:
            for n_comp in N_COMP_VALUES:
                oof = np.zeros_like(y, dtype=np.float64)

                for train_idx, valid_idx in logo.split(X_proc, y, groups):
                    preds = predict_local_pls(
                        X_train=X_proc[train_idx],
                        y_train=y[train_idx],
                        X_query=X_proc[valid_idx],
                        k=k,
                        n_comp=n_comp,
                    )
                    oof[valid_idx] = preds

                rmse = float(np.sqrt(mean_squared_error(y, oof)))
                results.append(
                    {
                        "preproc": preproc,
                        "k": k,
                        "n_comp": n_comp,
                        "loso_rmse": rmse,
                    }
                )
                done += 1
                print(f"[{done}/{total}] preproc={preproc} k={k} n_comp={n_comp} loso_rmse={rmse:.6f}")

    return pd.DataFrame(results).sort_values("loso_rmse", kind="stable").reset_index(drop=True)


def save_submission(
    sample_submit_df: pd.DataFrame,
    test_df: pd.DataFrame,
    sample_col: str,
    preds: np.ndarray,
    out_path: Path,
) -> None:
    pred_df = pd.DataFrame(
        {
            "sample_number": test_df[sample_col].to_numpy(),
            "prediction": preds,
        }
    )
    submission_df = sample_submit_df[["sample_number"]].merge(
        pred_df,
        on="sample_number",
        how="left",
        validate="one_to_one",
    )
    if submission_df["prediction"].isna().any():
        missing = submission_df.loc[submission_df["prediction"].isna(), "sample_number"].tolist()
        raise ValueError(f"Missing predictions for sample_number values: {missing}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    submission_df.to_csv(out_path, index=False, header=False, encoding=SUBMIT_ENCODING)


def main() -> None:
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)

    train_df, test_df, sample_submit_df, wave_cols, sample_col, species_col, target_col = load_data()
    band2_cols = select_band_columns(wave_cols, BAND2_RANGE)

    X_train = train_df[band2_cols].to_numpy(dtype=np.float64)
    y_train = train_df[target_col].to_numpy(dtype=np.float64)
    groups = train_df[species_col].to_numpy()
    X_test = test_df[band2_cols].to_numpy(dtype=np.float64)

    print(f"train_shape={train_df.shape}")
    print(f"test_shape={test_df.shape}")
    print(f"species_col={species_col}")
    print(f"target_col={target_col}")
    print(f"band2_range_cm-1={BAND2_RANGE}")
    print(f"band2_feature_count={len(band2_cols)}")
    print("")

    results_df = run_loso_grid(X_train, y_train, groups)
    results_df.to_csv(RESULTS_PATH, index=False, encoding="utf-8")

    print("")
    print("Top 10 configurations:")
    print(results_df.head(10).to_string(index=False))
    print("")
    print(f"saved_results={RESULTS_PATH}")

    best = results_df.iloc[0]
    best_preproc = str(best["preproc"])
    best_k = int(best["k"])
    best_n_comp = int(best["n_comp"])

    X_train_best = apply_preprocessing(X_train, best_preproc)
    X_test_best = apply_preprocessing(X_test, best_preproc)
    test_preds = predict_local_pls(
        X_train=X_train_best,
        y_train=y_train,
        X_query=X_test_best,
        k=best_k,
        n_comp=best_n_comp,
    )

    print(f"best_preproc={best_preproc}")
    print(f"best_k={best_k}")
    print(f"best_n_comp={best_n_comp}")
    print(f"best_loso_rmse={float(best['loso_rmse']):.6f}")
    print(f"test_pred_min={test_preds.min():.6f}")
    print(f"test_pred_max={test_preds.max():.6f}")

    if np.any(test_preds < 0):
        print("Negative predictions detected. Submission file was not generated.")
        return

    submission_path = SUBMISSIONS_DIR / (
        f"expLocalPLS_band2_{best_preproc}_k{best_k}_n{best_n_comp}_submission.csv"
    )
    save_submission(sample_submit_df, test_df, sample_col, test_preds, submission_path)
    print(f"saved_submission={submission_path}")


if __name__ == "__main__":
    main()
