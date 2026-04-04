from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.spectral_batch_utils import (
    GROUP_COL,
    TARGET_COL,
    apply_sg,
    candidate_interval_masks,
    load_test_df,
    load_train_df,
    rmse,
    save_submission,
    wave_columns,
)

EXPERIMENT_ID = "expA024_strong_batch"
EXPERIMENT_DIR = PROJECT_ROOT / "experiments" / EXPERIMENT_ID
SUBMISSION_DIR = PROJECT_ROOT / "submissions"


def fit_pls(x_train: np.ndarray, y_train: np.ndarray, x_valid: np.ndarray, n_components: int) -> np.ndarray:
    model = PLSRegression(n_components=n_components, max_iter=500)
    model.fit(x_train, y_train)
    return model.predict(x_valid).ravel()


def train_final_pls(x: np.ndarray, y: np.ndarray, x_test: np.ndarray, n_components: int) -> np.ndarray:
    model = PLSRegression(n_components=n_components, max_iter=500)
    model.fit(x, y)
    return model.predict(x_test).ravel()


def evaluate_cv(x: np.ndarray, y: np.ndarray, groups: np.ndarray, n_components: int, splitter) -> tuple[float, list[float]]:
    oof = np.zeros(len(y), dtype=float)
    fold_scores: list[float] = []
    for train_idx, valid_idx in splitter.split(x, y, groups):
        pred = fit_pls(x[train_idx], y[train_idx], x[valid_idx], n_components)
        oof[valid_idx] = pred
        fold_scores.append(rmse(y[valid_idx], pred))
    return rmse(y, oof), fold_scores


def run_ipls(x_train_raw: np.ndarray, x_test_raw: np.ndarray, y: np.ndarray, groups: np.ndarray) -> dict:
    x = apply_sg(x_train_raw, deriv=1)
    x_test = apply_sg(x_test_raw, deriv=1)
    masks = candidate_interval_masks(x.shape[1], n_intervals=20, pick_sizes=[1, 2, 3])
    best = None
    best_mask = None
    for mask in masks:
        if mask.sum() < 20:
            continue
        n_comp = min(10, int(mask.sum()) - 1)
        score, fold_scores = evaluate_cv(x[:, mask], y, groups, n_comp, GroupKFold(n_splits=5))
        if best is None or score < best["oof_rmse"]:
            best = {
                "experiment_id": "expA024_ipls_pls",
                "theme": "iPLS-style interval selection + PLS",
                "validation": "GroupKFold_species",
                "oof_rmse": score,
                "fold_scores": fold_scores,
                "best_params": {"selected_features": int(mask.sum()), "n_components": n_comp},
            }
            best_mask = mask.copy()
    preds = train_final_pls(x[:, best_mask], y, x_test[:, best_mask], best["best_params"]["n_components"])
    submission_path = SUBMISSION_DIR / "expA024_ipls_pls_submission.csv"
    save_submission(PROJECT_ROOT, preds, submission_path)
    best["submission_path"] = str(submission_path)
    return best


def run_water_band(x_train_raw: np.ndarray, x_test_raw: np.ndarray, y: np.ndarray, groups: np.ndarray) -> dict:
    x = apply_sg(x_train_raw, deriv=1)
    x_test = apply_sg(x_test_raw, deriv=1)
    ranges = [(350, 550), (750, 950), (1100, 1350), (350, 950)]
    best = None
    best_idx = None
    for left, right in ranges:
        idx = np.arange(left, min(right, x.shape[1]))
        n_comp = min(12, len(idx) - 1)
        score, fold_scores = evaluate_cv(x[:, idx], y, groups, n_comp, GroupKFold(n_splits=5))
        if best is None or score < best["oof_rmse"]:
            best = {
                "experiment_id": "expA025_water_band_pls",
                "theme": "Water-band-focused interval + PLS",
                "validation": "GroupKFold_species",
                "oof_rmse": score,
                "fold_scores": fold_scores,
                "best_params": {"left": int(left), "right": int(right), "n_components": n_comp},
            }
            best_idx = idx
    preds = train_final_pls(x[:, best_idx], y, x_test[:, best_idx], best["best_params"]["n_components"])
    submission_path = SUBMISSION_DIR / "expA025_water_band_pls_submission.csv"
    save_submission(PROJECT_ROOT, preds, submission_path)
    best["submission_path"] = str(submission_path)
    return best


def run_cars_like(x_train_raw: np.ndarray, x_test_raw: np.ndarray, y: np.ndarray, groups: np.ndarray) -> dict:
    x = apply_sg(x_train_raw, deriv=1)
    x_test = apply_sg(x_test_raw, deriv=1)
    candidates = [(12, 120), (12, 150), (15, 100), (15, 150)]
    best = None
    best_idx = None
    for n_comp, n_keep in candidates:
        oof = np.zeros(len(y), dtype=float)
        fold_scores: list[float] = []
        for train_idx, valid_idx in GroupKFold(n_splits=5).split(x, y, groups):
            pls = PLSRegression(n_components=n_comp, max_iter=500)
            pls.fit(x[train_idx], y[train_idx])
            idx = np.argsort(np.abs(pls.coef_).ravel())[::-1][:n_keep]
            pred = fit_pls(
                x[train_idx][:, idx],
                y[train_idx],
                x[valid_idx][:, idx],
                min(n_comp, len(idx) - 1),
            )
            oof[valid_idx] = pred
            fold_scores.append(rmse(y[valid_idx], pred))
        score = rmse(y, oof)
        if best is None or score < best["oof_rmse"]:
            pls_all = PLSRegression(n_components=n_comp, max_iter=500)
            pls_all.fit(x, y)
            best_idx = np.argsort(np.abs(pls_all.coef_).ravel())[::-1][:n_keep]
            best = {
                "experiment_id": "expA026_cars_like_pls",
                "theme": "CARS-like selection + PLS",
                "validation": "GroupKFold_species",
                "oof_rmse": score,
                "fold_scores": fold_scores,
                "best_params": {"n_components": n_comp, "n_keep": n_keep, "selected_features": n_keep},
            }
    preds = train_final_pls(
        x[:, best_idx],
        y,
        x_test[:, best_idx],
        min(best["best_params"]["n_components"], len(best_idx) - 1),
    )
    submission_path = SUBMISSION_DIR / "expA026_cars_like_pls_submission.csv"
    save_submission(PROJECT_ROOT, preds, submission_path)
    best["submission_path"] = str(submission_path)
    return best


def run_logo_base(x_train_raw: np.ndarray, x_test_raw: np.ndarray, y: np.ndarray, groups: np.ndarray) -> dict:
    x = apply_sg(x_train_raw, deriv=1)
    x_test = apply_sg(x_test_raw, deriv=1)
    candidates = [5, 8, 10, 12, 15]
    best = None
    for n_comp in candidates:
        score, fold_scores = evaluate_cv(x, y, groups, n_comp, LeaveOneGroupOut())
        if best is None or score < best["oof_rmse"]:
            best = {
                "experiment_id": "expA027_loso_sg1_pls",
                "theme": "SG1 + PLS with LOSO",
                "validation": "LeaveOneGroupOut_species",
                "oof_rmse": score,
                "fold_scores": fold_scores,
                "best_params": {"n_components": n_comp},
            }
    preds = train_final_pls(x, y, x_test, best["best_params"]["n_components"])
    submission_path = SUBMISSION_DIR / "expA027_loso_sg1_pls_submission.csv"
    save_submission(PROJECT_ROOT, preds, submission_path)
    best["submission_path"] = str(submission_path)
    return best


def run_preproc_ensemble(x_train_raw: np.ndarray, x_test_raw: np.ndarray, y: np.ndarray, groups: np.ndarray) -> dict:
    members = {
        "raw": x_train_raw,
        "sg1": apply_sg(x_train_raw, deriv=1),
        "sg2": apply_sg(x_train_raw, deriv=2),
    }
    members_test = {
        "raw": x_test_raw,
        "sg1": apply_sg(x_test_raw, deriv=1),
        "sg2": apply_sg(x_test_raw, deriv=2),
    }
    candidates = [5, 8, 10, 12]
    best = None
    for n_comp in candidates:
        oof = np.zeros(len(y), dtype=float)
        fold_scores: list[float] = []
        splitter = GroupKFold(n_splits=5)
        for train_idx, valid_idx in splitter.split(x_train_raw, y, groups):
            fold_preds = []
            for name, x_member in members.items():
                pred = fit_pls(x_member[train_idx], y[train_idx], x_member[valid_idx], n_comp)
                fold_preds.append(pred)
            pred_mean = np.mean(fold_preds, axis=0)
            oof[valid_idx] = pred_mean
            fold_scores.append(rmse(y[valid_idx], pred_mean))
        score = rmse(y, oof)
        if best is None or score < best["oof_rmse"]:
            best = {
                "experiment_id": "expA028_preproc_ensemble_pls",
                "theme": "Raw/SG1/SG2 PLS ensemble",
                "validation": "GroupKFold_species",
                "oof_rmse": score,
                "fold_scores": fold_scores,
                "best_params": {"n_components": n_comp, "members": ["raw", "sg1", "sg2"]},
            }
    test_preds = []
    for name, x_member in members.items():
        test_preds.append(train_final_pls(x_member, y, members_test[name], best["best_params"]["n_components"]))
    preds = np.mean(test_preds, axis=0)
    submission_path = SUBMISSION_DIR / "expA028_preproc_ensemble_pls_submission.csv"
    save_submission(PROJECT_ROOT, preds, submission_path)
    best["submission_path"] = str(submission_path)
    return best


def main() -> None:
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
    train_df = load_train_df(PROJECT_ROOT)
    test_df = load_test_df(PROJECT_ROOT)
    feature_cols = wave_columns()
    x_train_raw = train_df[feature_cols].to_numpy(dtype=np.float64)
    x_test_raw = test_df[feature_cols].to_numpy(dtype=np.float64)
    y = train_df[TARGET_COL].to_numpy(dtype=np.float64)
    groups = train_df[GROUP_COL].to_numpy()

    results = [
        run_ipls(x_train_raw, x_test_raw, y, groups),
        run_water_band(x_train_raw, x_test_raw, y, groups),
        run_cars_like(x_train_raw, x_test_raw, y, groups),
        run_logo_base(x_train_raw, x_test_raw, y, groups),
        run_preproc_ensemble(x_train_raw, x_test_raw, y, groups),
    ]

    rows = []
    for result in results:
        rows.append(
            {
                "experiment_id": result["experiment_id"],
                "theme": result["theme"],
                "validation": result["validation"],
                "oof_rmse": result["oof_rmse"],
                "fold_rmse_mean": float(np.mean(result["fold_scores"])),
                "fold_rmse_std": float(np.std(result["fold_scores"])),
                "best_params": json.dumps(result["best_params"], ensure_ascii=False),
                "submission_path": result["submission_path"],
            }
        )
    summary_df = pd.DataFrame(rows).sort_values("oof_rmse")
    summary_df.to_csv(EXPERIMENT_DIR / "summary.csv", index=False)

    lines = [
        f"# {EXPERIMENT_ID}",
        "",
        "| rank | experiment_id | theme | validation | oof_rmse | fold_mean | fold_std |",
        "| ---: | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for rank, (_, row) in enumerate(summary_df.iterrows(), start=1):
        lines.append(
            f"| {rank} | {row['experiment_id']} | {row['theme']} | {row['validation']} | "
            f"{row['oof_rmse']:.6f} | {row['fold_rmse_mean']:.6f} | {row['fold_rmse_std']:.6f} |"
        )
    (EXPERIMENT_DIR / "result.md").write_text("\n".join(lines), encoding="utf-8")
    print(summary_df.to_string(index=False))
    print(f"saved_summary={EXPERIMENT_DIR / 'summary.csv'}")
    print(f"saved_report={EXPERIMENT_DIR / 'result.md'}")


if __name__ == "__main__":
    main()
