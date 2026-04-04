from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.spectral_batch_utils import (
    ExperimentResult,
    GROUP_COL,
    ID_COL,
    TARGET_COL,
    apply_detrending,
    apply_msc,
    apply_sg,
    apply_snv,
    candidate_interval_masks,
    evaluate_group_model,
    evaluate_logo_model,
    fit_elastic_predict,
    fit_pls_predict,
    load_sample_submit,
    load_test_df,
    load_train_df,
    rmse,
    save_submission,
    top_corr_indices,
    vip_scores,
    wave_columns,
)

EXPERIMENT_ID = "expA010_research_batch12"
EXPERIMENT_DIR = PROJECT_ROOT / "experiments" / EXPERIMENT_ID
SUBMISSION_DIR = PROJECT_ROOT / "submissions"


def base_arrays():
    train_df = load_train_df(PROJECT_ROOT)
    test_df = load_test_df(PROJECT_ROOT)
    feature_cols = wave_columns()
    x_train_raw = train_df[feature_cols].to_numpy(dtype=np.float64)
    x_test_raw = test_df[feature_cols].to_numpy(dtype=np.float64)
    y = train_df[TARGET_COL].to_numpy(dtype=np.float64)
    groups = train_df[GROUP_COL].to_numpy()
    test_groups = test_df[GROUP_COL].to_numpy()
    return train_df, test_df, x_train_raw, x_test_raw, y, groups, test_groups


def train_final_pls(x: np.ndarray, y: np.ndarray, x_test: np.ndarray, n_components: int) -> np.ndarray:
    model = PLSRegression(n_components=n_components, max_iter=500)
    model.fit(x, y)
    return model.predict(x_test).ravel()


def summarize_result(
    experiment_id: str,
    theme: str,
    validation: str,
    best_params: dict,
    oof_rmse: float,
    fold_scores: list[float],
    submission_path: Path | None = None,
) -> ExperimentResult:
    return ExperimentResult(
        experiment_id=experiment_id,
        theme=theme,
        validation=validation,
        best_params=best_params,
        oof_rmse=oof_rmse,
        fold_rmse_mean=float(np.mean(fold_scores)),
        fold_rmse_std=float(np.std(fold_scores)),
        submission_path=submission_path,
    )


def run_snv_sg_pls(train_df, test_df, x_train_raw, x_test_raw, y, groups) -> ExperimentResult:
    experiment_id = "expA011_snv_sg_pls"
    x = apply_sg(apply_snv(x_train_raw), deriv=1)
    x_test = apply_sg(apply_snv(x_test_raw), deriv=1)
    candidates = [5, 8, 10, 12, 15]
    best = None
    for n_comp in candidates:
        oof_rmse, fold_scores, _ = evaluate_group_model(
            x, y, groups, lambda xt, yt, xv, gt: fit_pls_predict(xt, yt, xv, n_comp)
        )
        if best is None or oof_rmse < best[0]:
            best = (oof_rmse, fold_scores, n_comp)
    preds = train_final_pls(x, y, x_test, best[2])
    submission_path = SUBMISSION_DIR / f"{experiment_id}_submission.csv"
    save_submission(PROJECT_ROOT, preds, submission_path)
    return summarize_result(
        experiment_id, "SNV + SG derivative + PLS", "GroupKFold_species",
        {"n_components": best[2]}, best[0], best[1], submission_path
    )


def run_msc_sg_pls(train_df, test_df, x_train_raw, x_test_raw, y, groups) -> ExperimentResult:
    experiment_id = "expA012_msc_sg_pls"
    x = apply_sg(apply_msc(x_train_raw), deriv=1)
    x_test = apply_sg(apply_msc(x_test_raw), deriv=1)
    candidates = [5, 8, 10, 12, 15]
    best = None
    for n_comp in candidates:
        oof_rmse, fold_scores, _ = evaluate_group_model(
            x, y, groups, lambda xt, yt, xv, gt: fit_pls_predict(xt, yt, xv, n_comp)
        )
        if best is None or oof_rmse < best[0]:
            best = (oof_rmse, fold_scores, n_comp)
    preds = train_final_pls(x, y, x_test, best[2])
    submission_path = SUBMISSION_DIR / f"{experiment_id}_submission.csv"
    save_submission(PROJECT_ROOT, preds, submission_path)
    return summarize_result(
        experiment_id, "MSC + SG derivative + PLS", "GroupKFold_species",
        {"n_components": best[2]}, best[0], best[1], submission_path
    )


def run_detrend_pls(train_df, test_df, x_train_raw, x_test_raw, y, groups) -> ExperimentResult:
    experiment_id = "expA013_detrend_pls"
    x = apply_detrending(x_train_raw)
    x_test = apply_detrending(x_test_raw)
    candidates = [5, 8, 10, 12, 15, 20]
    best = None
    for n_comp in candidates:
        oof_rmse, fold_scores, _ = evaluate_group_model(
            x, y, groups, lambda xt, yt, xv, gt: fit_pls_predict(xt, yt, xv, n_comp)
        )
        if best is None or oof_rmse < best[0]:
            best = (oof_rmse, fold_scores, n_comp)
    preds = train_final_pls(x, y, x_test, best[2])
    submission_path = SUBMISSION_DIR / f"{experiment_id}_submission.csv"
    save_submission(PROJECT_ROOT, preds, submission_path)
    return summarize_result(
        experiment_id, "Detrending + PLS", "GroupKFold_species",
        {"n_components": best[2]}, best[0], best[1], submission_path
    )


def run_sg_param_pls(train_df, test_df, x_train_raw, x_test_raw, y, groups) -> ExperimentResult:
    experiment_id = "expA014_sg_param_pls"
    param_grid = [
        {"window": 9, "polyorder": 2, "deriv": 1, "n_components": 10},
        {"window": 11, "polyorder": 2, "deriv": 1, "n_components": 12},
        {"window": 15, "polyorder": 2, "deriv": 1, "n_components": 12},
        {"window": 11, "polyorder": 3, "deriv": 1, "n_components": 12},
        {"window": 11, "polyorder": 3, "deriv": 2, "n_components": 8},
    ]
    best = None
    for params in param_grid:
        x = apply_sg(x_train_raw, params["window"], params["polyorder"], params["deriv"])
        oof_rmse, fold_scores, _ = evaluate_group_model(
            x, y, groups,
            lambda xt, yt, xv, gt, n=params["n_components"]: fit_pls_predict(xt, yt, xv, n),
        )
        if best is None or oof_rmse < best[0]:
            best = (oof_rmse, fold_scores, params)
    x_best = apply_sg(
        x_train_raw, best[2]["window"], best[2]["polyorder"], best[2]["deriv"]
    )
    x_test_best = apply_sg(
        x_test_raw, best[2]["window"], best[2]["polyorder"], best[2]["deriv"]
    )
    preds = train_final_pls(x_best, y, x_test_best, best[2]["n_components"])
    submission_path = SUBMISSION_DIR / f"{experiment_id}_submission.csv"
    save_submission(PROJECT_ROOT, preds, submission_path)
    return summarize_result(
        experiment_id, "SG parameter sweep + PLS", "GroupKFold_species",
        best[2], best[0], best[1], submission_path
    )


def run_vip_pls(train_df, test_df, x_train_raw, x_test_raw, y, groups) -> ExperimentResult:
    experiment_id = "expA015_vip_pls"
    x = apply_sg(x_train_raw, deriv=1)
    x_test = apply_sg(x_test_raw, deriv=1)
    candidates = [(12, 0.9), (12, 1.0), (12, 1.1), (15, 0.9), (15, 1.0)]
    best = None

    def fit_predict_vip(xt, yt, xv, n_comp, vip_threshold):
        pls = PLSRegression(n_components=n_comp, max_iter=500)
        pls.fit(xt, yt)
        scores = vip_scores(pls, xt, yt)
        mask = scores >= vip_threshold
        if mask.sum() < max(10, n_comp):
            mask[np.argsort(scores)[::-1][: max(10, n_comp)]] = True
        pls2 = PLSRegression(n_components=min(n_comp, int(mask.sum()) - 1), max_iter=500)
        pls2.fit(xt[:, mask], yt)
        return pls2.predict(xv[:, mask]).ravel(), mask

    best_mask = None
    for n_comp, vip_threshold in candidates:
        fold_masks = []

        def runner(xt, yt, xv, gt):
            pred, mask = fit_predict_vip(xt, yt, xv, n_comp, vip_threshold)
            fold_masks.append(mask)
            return pred

        oof_rmse, fold_scores, _ = evaluate_group_model(x, y, groups, runner)
        if best is None or oof_rmse < best[0]:
            best = (oof_rmse, fold_scores, {"n_components": n_comp, "vip_threshold": vip_threshold})
            best_mask = fold_masks

    pls = PLSRegression(n_components=best[2]["n_components"], max_iter=500)
    pls.fit(x, y)
    scores = vip_scores(pls, x, y)
    mask = scores >= best[2]["vip_threshold"]
    if mask.sum() < max(10, best[2]["n_components"]):
        mask[np.argsort(scores)[::-1][: max(10, best[2]["n_components"])]] = True
    preds = train_final_pls(
        x[:, mask], y, x_test[:, mask], min(best[2]["n_components"], int(mask.sum()) - 1)
    )
    submission_path = SUBMISSION_DIR / f"{experiment_id}_submission.csv"
    save_submission(PROJECT_ROOT, preds, submission_path)
    best[2]["selected_features"] = int(mask.sum())
    return summarize_result(
        experiment_id, "VIP selection + PLS", "GroupKFold_species",
        best[2], best[0], best[1], submission_path
    )


def run_cars_pls(train_df, test_df, x_train_raw, x_test_raw, y, groups) -> ExperimentResult:
    experiment_id = "expA016_cars_like_pls"
    x = apply_sg(x_train_raw, deriv=1)
    x_test = apply_sg(x_test_raw, deriv=1)
    candidates = [(12, 200), (12, 120), (15, 200), (15, 100)]
    best = None

    def select_cars_like(xt, yt, n_comp, n_keep):
        pls = PLSRegression(n_components=n_comp, max_iter=500)
        pls.fit(xt, yt)
        coef_rank = np.argsort(np.abs(pls.coef_).ravel())[::-1]
        return coef_rank[:n_keep]

    for n_comp, n_keep in candidates:
        def runner(xt, yt, xv, gt):
            idx = select_cars_like(xt, yt, n_comp, n_keep)
            return fit_pls_predict(xt[:, idx], yt, xv[:, idx], min(n_comp, len(idx) - 1))

        oof_rmse, fold_scores, _ = evaluate_group_model(x, y, groups, runner)
        params = {"n_components": n_comp, "n_keep": n_keep}
        if best is None or oof_rmse < best[0]:
            best = (oof_rmse, fold_scores, params)
    idx = select_cars_like(x, y, best[2]["n_components"], best[2]["n_keep"])
    preds = train_final_pls(x[:, idx], y, x_test[:, idx], min(best[2]["n_components"], len(idx) - 1))
    submission_path = SUBMISSION_DIR / f"{experiment_id}_submission.csv"
    save_submission(PROJECT_ROOT, preds, submission_path)
    return summarize_result(
        experiment_id, "CARS-like selection + PLS", "GroupKFold_species",
        {**best[2], "selected_features": int(len(idx))}, best[0], best[1], submission_path
    )


def run_ipls_pls(train_df, test_df, x_train_raw, x_test_raw, y, groups) -> ExperimentResult:
    experiment_id = "expA017_ipls_pls"
    x = apply_sg(x_train_raw, deriv=1)
    x_test = apply_sg(x_test_raw, deriv=1)
    masks = candidate_interval_masks(x.shape[1], n_intervals=20, pick_sizes=[1, 2, 3])
    best = None
    best_mask = None
    for mask in masks:
        if mask.sum() < 20:
            continue
        n_comp = min(10, int(mask.sum()) - 1)
        oof_rmse, fold_scores, _ = evaluate_group_model(
            x[:, mask], y, groups, lambda xt, yt, xv, gt: fit_pls_predict(xt, yt, xv, n_comp)
        )
        if best is None or oof_rmse < best[0]:
            best = (oof_rmse, fold_scores, {"selected_features": int(mask.sum()), "n_components": n_comp})
            best_mask = mask.copy()
    preds = train_final_pls(x[:, best_mask], y, x_test[:, best_mask], best[2]["n_components"])
    submission_path = SUBMISSION_DIR / f"{experiment_id}_submission.csv"
    save_submission(PROJECT_ROOT, preds, submission_path)
    return summarize_result(
        experiment_id, "iPLS-style interval selection + PLS", "GroupKFold_species",
        best[2], best[0], best[1], submission_path
    )


def run_water_band_pls(train_df, test_df, x_train_raw, x_test_raw, y, groups) -> ExperimentResult:
    experiment_id = "expA018_water_band_pls"
    x = apply_sg(x_train_raw, deriv=1)
    x_test = apply_sg(x_test_raw, deriv=1)
    ranges = [(350, 550), (750, 950), (1100, 1350), (350, 950)]
    best = None
    best_idx = None
    for left, right in ranges:
        idx = np.arange(left, min(right, x.shape[1]))
        n_comp = min(12, len(idx) - 1)
        oof_rmse, fold_scores, _ = evaluate_group_model(
            x[:, idx], y, groups, lambda xt, yt, xv, gt: fit_pls_predict(xt, yt, xv, n_comp)
        )
        params = {"left": int(left), "right": int(right), "n_components": int(n_comp)}
        if best is None or oof_rmse < best[0]:
            best = (oof_rmse, fold_scores, params)
            best_idx = idx
    preds = train_final_pls(x[:, best_idx], y, x_test[:, best_idx], best[2]["n_components"])
    submission_path = SUBMISSION_DIR / f"{experiment_id}_submission.csv"
    save_submission(PROJECT_ROOT, preds, submission_path)
    return summarize_result(
        experiment_id, "Water-band-focused interval + PLS", "GroupKFold_species",
        best[2], best[0], best[1], submission_path
    )


def run_elasticnet(train_df, test_df, x_train_raw, x_test_raw, y, groups) -> ExperimentResult:
    experiment_id = "expA019_elasticnet_preproc"
    preprocessors = {
        "raw": lambda z: z,
        "snv": apply_snv,
        "deriv1": lambda z: apply_sg(z, deriv=1),
        "snv_deriv1": lambda z: apply_sg(apply_snv(z), deriv=1),
    }
    params_grid = [(0.01, 0.2), (0.01, 0.5), (0.05, 0.2)]
    best = None
    best_x = None
    best_x_test = None
    for name, transform in preprocessors.items():
        x = transform(x_train_raw)
        x_test = transform(x_test_raw)
        for alpha, l1_ratio in params_grid:
            oof_rmse, fold_scores, _ = evaluate_group_model(
                x, y, groups,
                lambda xt, yt, xv, gt, a=alpha, l=l1_ratio: fit_elastic_predict(xt, yt, xv, a, l),
            )
            params = {"preprocessing": name, "alpha": alpha, "l1_ratio": l1_ratio}
            if best is None or oof_rmse < best[0]:
                best = (oof_rmse, fold_scores, params)
                best_x = x
                best_x_test = x_test
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(best_x)
    x_test_scaled = scaler.transform(best_x_test)
    from sklearn.linear_model import ElasticNet
    model = ElasticNet(
        alpha=best[2]["alpha"], l1_ratio=best[2]["l1_ratio"], max_iter=5000, random_state=42
    )
    model.fit(x_scaled, y)
    preds = model.predict(x_test_scaled)
    submission_path = SUBMISSION_DIR / f"{experiment_id}_submission.csv"
    save_submission(PROJECT_ROOT, preds, submission_path)
    return summarize_result(
        experiment_id, "Elastic Net with preprocessing variants", "GroupKFold_species",
        best[2], best[0], best[1], submission_path
    )


def run_logo_eval(train_df, test_df, x_train_raw, x_test_raw, y, groups) -> ExperimentResult:
    experiment_id = "expA020_logo_eval"
    x = apply_sg(x_train_raw, deriv=1)
    x_test = apply_sg(x_test_raw, deriv=1)
    n_comp = 12
    oof_rmse, fold_scores, _ = evaluate_logo_model(
        x, y, groups, lambda xt, yt, xv, gt: fit_pls_predict(xt, yt, xv, n_comp)
    )
    preds = train_final_pls(x, y, x_test, n_comp)
    submission_path = SUBMISSION_DIR / f"{experiment_id}_submission.csv"
    save_submission(PROJECT_ROOT, preds, submission_path)
    return summarize_result(
        experiment_id, "Leave-One-Species-Out evaluation", "LeaveOneGroupOut_species",
        {"base_model": "SG derivative + PLS", "n_components": n_comp},
        oof_rmse, fold_scores, submission_path
    )


def run_blend() -> ExperimentResult:
    experiment_id = "expA021_blend"
    sources = [
        SUBMISSION_DIR / "expA004_snv_pls_submission.csv",
        SUBMISSION_DIR / "expA005_deriv_corr_pls_submission.csv",
        SUBMISSION_DIR / "expA008_deriv_ridge_submission.csv",
    ]
    sample = load_sample_submit(PROJECT_ROOT)
    pred_arrays = []
    for path in sources:
        df = pd.read_csv(path, header=None, names=[ID_COL, TARGET_COL])
        pred_arrays.append(df[TARGET_COL].to_numpy(dtype=float))
    blend_pred = np.mean(pred_arrays, axis=0)
    submission_path = SUBMISSION_DIR / f"{experiment_id}_submission.csv"
    sample[TARGET_COL] = blend_pred
    submission_path.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(submission_path, index=False, header=False)
    return summarize_result(
        experiment_id, "Blend / ensemble of strong submissions", "submission_blend_only",
        {"sources": [p.name for p in sources]}, float("nan"), [float("nan")], submission_path
    )


def run_species_aware(train_df, test_df, x_train_raw, x_test_raw, y, groups, test_groups) -> ExperimentResult:
    experiment_id = "expA022_species_aware_hierarchical"
    x = apply_sg(x_train_raw, deriv=1)
    x_test = apply_sg(x_test_raw, deriv=1)
    n_comp = 12

    def runner(xt, yt, xv, gt):
        pls = PLSRegression(n_components=n_comp, max_iter=500)
        pls.fit(xt, yt)
        pred_train = pls.predict(xt).ravel()
        residuals = yt - pred_train
        offsets = {}
        for g in np.unique(gt):
            offsets[g] = float(residuals[gt == g].mean())
        pred_valid = pls.predict(xv).ravel()
        return pred_valid

    oof_rmse, fold_scores, _ = evaluate_group_model(x, y, groups, runner)

    pls = PLSRegression(n_components=n_comp, max_iter=500)
    pls.fit(x, y)
    train_pred = pls.predict(x).ravel()
    residuals = y - train_pred
    offsets = {g: float(residuals[groups == g].mean()) for g in np.unique(groups)}
    preds = pls.predict(x_test).ravel()
    preds = preds + np.array([offsets.get(g, 0.0) for g in test_groups])
    submission_path = SUBMISSION_DIR / f"{experiment_id}_submission.csv"
    save_submission(PROJECT_ROOT, preds, submission_path)
    return summarize_result(
        experiment_id, "Species-aware local or hierarchical modeling", "GroupKFold_species",
        {"base_model": "SG derivative + PLS", "n_components": n_comp, "adjustment": "species residual offset"},
        oof_rmse, fold_scores, submission_path
    )


def main() -> None:
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
    train_df, test_df, x_train_raw, x_test_raw, y, groups, test_groups = base_arrays()

    results = [
        run_snv_sg_pls(train_df, test_df, x_train_raw, x_test_raw, y, groups),
        run_msc_sg_pls(train_df, test_df, x_train_raw, x_test_raw, y, groups),
        run_detrend_pls(train_df, test_df, x_train_raw, x_test_raw, y, groups),
        run_sg_param_pls(train_df, test_df, x_train_raw, x_test_raw, y, groups),
        run_vip_pls(train_df, test_df, x_train_raw, x_test_raw, y, groups),
        run_cars_pls(train_df, test_df, x_train_raw, x_test_raw, y, groups),
        run_ipls_pls(train_df, test_df, x_train_raw, x_test_raw, y, groups),
        run_water_band_pls(train_df, test_df, x_train_raw, x_test_raw, y, groups),
        run_elasticnet(train_df, test_df, x_train_raw, x_test_raw, y, groups),
        run_logo_eval(train_df, test_df, x_train_raw, x_test_raw, y, groups),
        run_blend(),
        run_species_aware(train_df, test_df, x_train_raw, x_test_raw, y, groups, test_groups),
    ]

    rows = []
    for result in results:
        row = {
            "experiment_id": result.experiment_id,
            "theme": result.theme,
            "validation": result.validation,
            "oof_rmse": result.oof_rmse,
            "fold_rmse_mean": result.fold_rmse_mean,
            "fold_rmse_std": result.fold_rmse_std,
            "best_params": json.dumps(result.best_params, ensure_ascii=False),
            "submission_path": str(result.submission_path) if result.submission_path else "",
        }
        rows.append(row)
    summary_df = pd.DataFrame(rows)
    summary_df.to_csv(EXPERIMENT_DIR / "summary.csv", index=False)

    ranked_df = summary_df[np.isfinite(summary_df["oof_rmse"])].sort_values("oof_rmse")
    report_lines = [
        f"# {EXPERIMENT_ID}",
        "",
        "## Ranking",
        "",
        "| rank | experiment_id | theme | validation | oof_rmse | fold_mean | fold_std |",
        "| ---: | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for rank, (_, row) in enumerate(ranked_df.iterrows(), start=1):
        report_lines.append(
            f"| {rank} | {row['experiment_id']} | {row['theme']} | {row['validation']} | "
            f"{row['oof_rmse']:.6f} | {row['fold_rmse_mean']:.6f} | {row['fold_rmse_std']:.6f} |"
        )
    report_lines.extend(
        [
            "",
            "## Non-OOF Items",
            "",
            "- `expA021_blend`: submission-only ensemble of existing strong submissions",
            "",
            "## Files",
            "",
            f"- summary csv: `{EXPERIMENT_DIR / 'summary.csv'}`",
        ]
    )
    (EXPERIMENT_DIR / "result.md").write_text("\n".join(report_lines), encoding="utf-8")
    print(summary_df.to_string(index=False))
    print(f"saved_summary={EXPERIMENT_DIR / 'summary.csv'}")
    print(f"saved_report={EXPERIMENT_DIR / 'result.md'}")


if __name__ == "__main__":
    main()
