from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.decomposition import PCA
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GroupKFold


PROJECT_ROOT = Path(r"C:/workspace/ai-os/competitions/near-infrared-challenge")
TRAIN_PATH = PROJECT_ROOT / "data" / "raw" / "train.csv"
TEST_PATH = PROJECT_ROOT / "data" / "raw" / "test.csv"
N_COMPONENTS = 15
N_SPLITS = 5
TARGET_RMSE = 4.08


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    train_df = pd.read_csv(TRAIN_PATH, encoding="cp932")
    test_df = pd.read_csv(TEST_PATH, encoding="cp932")
    feature_cols = list(train_df.columns[4:])
    test_feature_cols = list(test_df.columns[3:])
    if feature_cols != test_feature_cols:
        raise ValueError("Train and test feature columns do not match.")
    return train_df, test_df, feature_cols


def snv_transform(x: np.ndarray) -> np.ndarray:
    row_mean = x.mean(axis=1, keepdims=True)
    row_std = x.std(axis=1, keepdims=True)
    return (x - row_mean) / np.clip(row_std, 1e-12, None)


def msc_transform(x: np.ndarray, reference: np.ndarray) -> np.ndarray:
    corrected = np.empty_like(x, dtype=np.float64)
    for i, row in enumerate(x):
        slope, intercept = np.polyfit(reference, row, 1)
        slope = slope if abs(slope) > 1e-12 else 1e-12
        corrected[i] = (row - intercept) / slope
    return corrected


def fit_predict_pls(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_valid: np.ndarray,
    n_components: int = N_COMPONENTS,
) -> np.ndarray:
    n_comp = min(n_components, x_train.shape[0] - 1, x_train.shape[1])
    if n_comp < 1:
        raise ValueError("PLS n_components became < 1.")
    model = PLSRegression(n_components=n_comp, max_iter=500)
    model.fit(x_train, y_train)
    return model.predict(x_valid).ravel()


def evaluate_groupkfold(
    x: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
) -> dict[str, object]:
    splitter = GroupKFold(n_splits=N_SPLITS)
    oof = np.zeros(len(y), dtype=np.float64)
    fold_scores: list[float] = []

    for fold, (train_idx, valid_idx) in enumerate(splitter.split(x, y, groups), start=1):
        pred = fit_predict_pls(x[train_idx], y[train_idx], x[valid_idx], N_COMPONENTS)
        fold_rmse = rmse(y[valid_idx], pred)
        oof[valid_idx] = pred
        fold_scores.append(fold_rmse)
        print(f"  fold{fold}: rmse={fold_rmse:.6f} train={len(train_idx)} valid={len(valid_idx)}")

    return {
        "oof_rmse": rmse(y, oof),
        "fold_scores": fold_scores,
        "fold_mean": float(np.mean(fold_scores)),
        "fold_std": float(np.std(fold_scores)),
        "n_samples": int(len(y)),
        "n_groups": int(pd.Series(groups).nunique()),
    }


def evaluate_with_custom_transform(
    x: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    fold_transform_fn,
) -> dict[str, object]:
    splitter = GroupKFold(n_splits=N_SPLITS)
    oof = np.zeros(len(y), dtype=np.float64)
    fold_scores: list[float] = []

    for fold, (train_idx, valid_idx) in enumerate(splitter.split(x, y, groups), start=1):
        x_train, x_valid = fold_transform_fn(train_idx, valid_idx)
        pred = fit_predict_pls(x_train, y[train_idx], x_valid, N_COMPONENTS)
        fold_rmse = rmse(y[valid_idx], pred)
        oof[valid_idx] = pred
        fold_scores.append(fold_rmse)
        print(f"  fold{fold}: rmse={fold_rmse:.6f} train={len(train_idx)} valid={len(valid_idx)}")

    return {
        "oof_rmse": rmse(y, oof),
        "fold_scores": fold_scores,
        "fold_mean": float(np.mean(fold_scores)),
        "fold_std": float(np.std(fold_scores)),
        "n_samples": int(len(y)),
        "n_groups": int(pd.Series(groups).nunique()),
    }


def print_summary(name: str, result: dict[str, object]) -> None:
    fold_scores = ", ".join(f"{score:.6f}" for score in result["fold_scores"])
    print(
        f"{name}: OOF RMSE={result['oof_rmse']:.6f}, "
        f"fold mean={result['fold_mean']:.6f}, fold std={result['fold_std']:.6f}"
    )
    print(f"  fold scores=[{fold_scores}]")


def experiment_a(
    x_train: np.ndarray,
    x_test: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
) -> dict[str, dict[str, object] | float]:
    print("\n[Experiment A] SNV transductive")
    x_train_snv = snv_transform(x_train)
    x_test_snv = snv_transform(x_test)

    train_only_res = evaluate_groupkfold(x_train_snv, y, groups)
    transductive_train_snv = snv_transform(np.vstack([x_train, x_test]))[: len(x_train)]
    transductive_res = evaluate_groupkfold(transductive_train_snv, y, groups)

    max_abs_diff_train = float(np.max(np.abs(x_train_snv - transductive_train_snv)))
    max_abs_diff_test = float(np.max(np.abs(x_test_snv - snv_transform(np.vstack([x_train, x_test])[len(x_train):]))))
    print_summary("  SNV train-only", train_only_res)
    print_summary("  SNV train+test", transductive_res)
    print(f"  max_abs_diff_train={max_abs_diff_train:.12f}")
    print(f"  max_abs_diff_test={max_abs_diff_test:.12f}")

    return {
        "train_only": train_only_res,
        "train_plus_test": transductive_res,
        "max_abs_diff_train": max_abs_diff_train,
        "max_abs_diff_test": max_abs_diff_test,
    }


def experiment_b(
    x_train: np.ndarray,
    x_test: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
) -> dict[str, dict[str, object]]:
    print("\n[Experiment B] MSC transductive")
    full_reference = np.vstack([x_train, x_test]).mean(axis=0)

    def baseline_transform(train_idx: np.ndarray, valid_idx: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        ref = x_train[train_idx].mean(axis=0)
        return msc_transform(x_train[train_idx], ref), msc_transform(x_train[valid_idx], ref)

    def transductive_transform(train_idx: np.ndarray, valid_idx: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        return msc_transform(x_train[train_idx], full_reference), msc_transform(x_train[valid_idx], full_reference)

    baseline_res = evaluate_with_custom_transform(x_train, y, groups, baseline_transform)
    transductive_res = evaluate_with_custom_transform(x_train, y, groups, transductive_transform)
    print_summary("  MSC baseline", baseline_res)
    print_summary("  MSC transductive", transductive_res)
    print(f"  delta_oof={transductive_res['oof_rmse'] - baseline_res['oof_rmse']:.6f}")
    return {
        "baseline": baseline_res,
        "transductive": transductive_res,
    }


def experiment_c(
    x_train: np.ndarray,
    x_test: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
) -> list[dict[str, object]]:
    print("\n[Experiment C] Near-test subset training")
    test_median = np.median(x_test, axis=0)
    distances = np.linalg.norm(x_train - test_median[None, :], axis=1)
    sorted_idx = np.argsort(distances)
    n_candidates = [200, 400, 600, 800, len(x_train)]
    results: list[dict[str, object]] = []

    for n_keep in n_candidates:
        keep_idx = sorted_idx[:n_keep]
        keep_groups = groups[keep_idx]
        unique_groups = np.unique(keep_groups)
        print(f"  N={n_keep}: n_groups={len(unique_groups)}")
        if len(unique_groups) < N_SPLITS:
            result = {
                "n_keep": n_keep,
                "status": "skipped",
                "reason": f"unique_groups={len(unique_groups)} < {N_SPLITS}",
            }
            print(f"    skipped: {result['reason']}")
            results.append(result)
            continue

        res = evaluate_groupkfold(x_train[keep_idx], y[keep_idx], keep_groups)
        res["n_keep"] = n_keep
        res["mean_distance"] = float(distances[keep_idx].mean())
        print_summary(f"    subset N={n_keep}", res)
        results.append(res)

    return results


def remove_epo_components(
    x: np.ndarray,
    species_means: np.ndarray,
    n_remove: int,
) -> np.ndarray:
    pca = PCA(n_components=n_remove, svd_solver="full")
    pca.fit(species_means)
    x_centered = x - pca.mean_
    projection = x_centered @ pca.components_.T @ pca.components_
    residual = x_centered - projection
    return residual + pca.mean_


def experiment_d(
    x_train: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
) -> list[dict[str, object]]:
    print("\n[Experiment D] EPO-like species-direction removal")
    species_ids = np.sort(pd.unique(groups))
    species_means = np.vstack([x_train[groups == species_id].mean(axis=0) for species_id in species_ids])
    results: list[dict[str, object]] = []

    for k in [1, 2, 3, 5]:
        x_res = remove_epo_components(x_train, species_means, k)
        res = evaluate_groupkfold(x_res, y, groups)
        res["k_remove"] = k
        print_summary(f"  EPO k={k}", res)
        results.append(res)

    return results


def build_conclusion(
    baseline_res: dict[str, object],
    exp_a: dict[str, dict[str, object] | float],
    exp_b: dict[str, dict[str, object]],
    exp_c: list[dict[str, object]],
    exp_d: list[dict[str, object]],
) -> str:
    candidates: list[tuple[str, float]] = [("Baseline raw PLS(15)", float(baseline_res["oof_rmse"]))]
    candidates.append(("A SNV train-only", float(exp_a["train_only"]["oof_rmse"])))
    candidates.append(("A SNV train+test", float(exp_a["train_plus_test"]["oof_rmse"])))
    candidates.append(("B MSC baseline", float(exp_b["baseline"]["oof_rmse"])))
    candidates.append(("B MSC transductive", float(exp_b["transductive"]["oof_rmse"])))

    for row in exp_c:
        if row.get("status") == "skipped":
            continue
        candidates.append((f"C subset N={row['n_keep']}", float(row["oof_rmse"])))

    for row in exp_d:
        candidates.append((f"D EPO k={row['k_remove']}", float(row["oof_rmse"])))

    best_name, best_rmse = min(candidates, key=lambda x: x[1])
    gap_to_target = best_rmse - TARGET_RMSE
    baseline_gap = float(baseline_res["oof_rmse"]) - best_rmse
    lines = [
        "H5 conclusion",
        f"- Best in this H5 set: {best_name} with OOF RMSE={best_rmse:.6f}.",
        f"- Improvement vs raw PLS(15) baseline: {baseline_gap:.6f} RMSE lower.",
        f"- Distance to RMSE=4.08: {gap_to_target:.6f}.",
    ]

    if gap_to_target <= 0:
        lines.append("- This set of domain-adaptation experiments reached or exceeded 4.08.")
    elif gap_to_target < 1.0:
        lines.append("- This gets close to 4.08, but still does not reach it.")
    else:
        lines.append("- This does not get close to 4.08; the gap remains large.")

    if exp_a["max_abs_diff_train"] < 1e-10 and exp_a["max_abs_diff_test"] < 1e-10:
        lines.append("- SNV transductive behaved exactly as expected: effectively no numerical difference.")

    return "\n".join(lines)


def main() -> None:
    train_df, test_df, feature_cols = load_data()
    x_train = train_df[feature_cols].to_numpy(dtype=np.float64)
    x_test = test_df[feature_cols].to_numpy(dtype=np.float64)
    y = train_df.iloc[:, 3].to_numpy(dtype=np.float64)
    groups = train_df.iloc[:, 1].to_numpy()

    print("expH5_domain_adapt")
    print(f"train_path={TRAIN_PATH}")
    print(f"test_path={TEST_PATH}")
    print(f"n_train={len(train_df)} n_test={len(test_df)} n_features={len(feature_cols)} n_groups={pd.Series(groups).nunique()}")
    print(f"PLS n_components={N_COMPONENTS}")

    print("\n[Baseline] Raw PLS(15)")
    baseline_res = evaluate_groupkfold(x_train, y, groups)
    print_summary("  Raw PLS(15)", baseline_res)

    exp_a = experiment_a(x_train, x_test, y, groups)
    exp_b = experiment_b(x_train, x_test, y, groups)
    exp_c = experiment_c(x_train, x_test, y, groups)
    exp_d = experiment_d(x_train, y, groups)

    print("\n[Summary Table]")
    print("name,oof_rmse,fold_mean,fold_std")
    print(f"baseline_raw_pls,{baseline_res['oof_rmse']:.6f},{baseline_res['fold_mean']:.6f},{baseline_res['fold_std']:.6f}")
    print(f"expA_snv_train_only,{exp_a['train_only']['oof_rmse']:.6f},{exp_a['train_only']['fold_mean']:.6f},{exp_a['train_only']['fold_std']:.6f}")
    print(f"expA_snv_train_plus_test,{exp_a['train_plus_test']['oof_rmse']:.6f},{exp_a['train_plus_test']['fold_mean']:.6f},{exp_a['train_plus_test']['fold_std']:.6f}")
    print(f"expB_msc_baseline,{exp_b['baseline']['oof_rmse']:.6f},{exp_b['baseline']['fold_mean']:.6f},{exp_b['baseline']['fold_std']:.6f}")
    print(f"expB_msc_transductive,{exp_b['transductive']['oof_rmse']:.6f},{exp_b['transductive']['fold_mean']:.6f},{exp_b['transductive']['fold_std']:.6f}")

    for row in exp_c:
        if row.get("status") == "skipped":
            print(f"expC_subset_{row['n_keep']},skipped,skipped,skipped")
        else:
            print(f"expC_subset_{row['n_keep']},{row['oof_rmse']:.6f},{row['fold_mean']:.6f},{row['fold_std']:.6f}")

    for row in exp_d:
        print(f"expD_epo_k{row['k_remove']},{row['oof_rmse']:.6f},{row['fold_mean']:.6f},{row['fold_std']:.6f}")

    conclusion = build_conclusion(baseline_res, exp_a, exp_b, exp_c, exp_d)
    print(f"\n{conclusion}")


if __name__ == "__main__":
    main()
