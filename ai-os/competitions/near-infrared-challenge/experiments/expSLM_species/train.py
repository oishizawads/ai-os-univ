from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TRAIN_PATH = PROJECT_ROOT / "data" / "raw" / "train.csv"
TEST_PATH = PROJECT_ROOT / "data" / "raw" / "test.csv"
RESULTS_PATH = Path(__file__).resolve().parent / "results.csv"
OOF_PATH = Path(__file__).resolve().parent / "oof_predictions.csv"
ENCODING = "cp932"

ID_COL_IDX = 0
SPECIES_ID_COL_IDX = 1
SPECIES_NAME_COL_IDX = 2
TARGET_COL_IDX = 3
WAVE_START_COL_IDX = 4

BAND2_RANGE = (4800.0, 5350.0)
PLS_COMPONENTS = 10
RIDGE_ALPHA = 1.0
FUSION_WEIGHTS = [0.3, 0.5, 0.7, 0.9]


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def snv(x: np.ndarray) -> np.ndarray:
    mu = x.mean(axis=1, keepdims=True)
    sd = x.std(axis=1, keepdims=True) + 1e-10
    return (x - mu) / sd


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, str, str, str, list[str]]:
    train_df = pd.read_csv(TRAIN_PATH, encoding=ENCODING)
    test_df = pd.read_csv(TEST_PATH, encoding=ENCODING)
    species_id_col = train_df.columns[SPECIES_ID_COL_IDX]
    species_name_col = train_df.columns[SPECIES_NAME_COL_IDX]
    target_col = train_df.columns[TARGET_COL_IDX]
    wave_cols = train_df.columns[WAVE_START_COL_IDX:].tolist()
    return train_df, test_df, species_id_col, species_name_col, target_col, wave_cols


def print_species_catalog(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    species_id_col: str,
    species_name_col: str,
) -> None:
    print("[Species names: train]")
    train_species = (
        train_df[[species_id_col, species_name_col]]
        .drop_duplicates()
        .sort_values(species_id_col)
        .reset_index(drop=True)
    )
    print(train_species.to_string(index=False))
    print("")

    print("[Species names: test]")
    test_species = (
        test_df[[species_id_col, species_name_col]]
        .drop_duplicates()
        .sort_values(species_id_col)
        .reset_index(drop=True)
    )
    print(test_species.to_string(index=False))
    print("")


def build_species_embeddings(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    species_name_col: str,
) -> tuple[np.ndarray, np.ndarray, str, int]:
    train_names = train_df[species_name_col].astype(str).tolist()
    test_names = test_df[species_name_col].astype(str).tolist()
    unique_names = pd.Index(train_names + test_names).unique().tolist()

    if SentenceTransformer is not None:
        model_name = "paraphrase-multilingual-MiniLM-L12-v2"
        encoder = SentenceTransformer(model_name)
        name_to_emb = {
            name: emb
            for name, emb in zip(unique_names, encoder.encode(unique_names, convert_to_numpy=True))
        }
        embedding_name = f"sentence-transformers:{model_name}"
    else:
        vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(1, 3))
        mat = vectorizer.fit_transform(unique_names).toarray().astype(np.float64)
        name_to_emb = {name: emb for name, emb in zip(unique_names, mat)}
        embedding_name = "sklearn:TfidfVectorizer(char, ngram_range=(1,3))"

    train_emb = np.vstack([name_to_emb[name] for name in train_names]).astype(np.float64)
    test_emb = np.vstack([name_to_emb[name] for name in test_names]).astype(np.float64)
    return train_emb, test_emb, embedding_name, int(train_emb.shape[1])


def select_band2(wave_cols: list[str], x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    wn = np.array([float(col) for col in wave_cols], dtype=np.float64)
    mask = (wn >= BAND2_RANGE[0]) & (wn <= BAND2_RANGE[1])
    return x[:, mask], wn[mask]


def fit_pls_model(
    x_train: np.ndarray,
    y_train: np.ndarray,
    n_components: int = PLS_COMPONENTS,
) -> PLSRegression | None:
    n_comp = min(n_components, x_train.shape[1], x_train.shape[0] - 1)
    if n_comp < 1:
        return None

    model = PLSRegression(n_components=n_comp, max_iter=500)
    model.fit(x_train, y_train)
    return model


def fit_ridge_predict(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_valid: np.ndarray,
    alpha: float = RIDGE_ALPHA,
) -> np.ndarray:
    model = make_pipeline(StandardScaler(), Ridge(alpha=alpha))
    model.fit(x_train, y_train)
    return model.predict(x_valid).astype(np.float64)


def evaluate_models(
    x_spec: np.ndarray,
    x_emb: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    logo = LeaveOneGroupOut()
    n_samples = len(y)

    oof_map: dict[str, np.ndarray] = {
        "A_spec_only": np.zeros(n_samples, dtype=np.float64),
        "B_species_only": np.zeros(n_samples, dtype=np.float64),
        "D_concat_pls_scores_emb": np.zeros(n_samples, dtype=np.float64),
    }
    for w in FUSION_WEIGHTS:
        oof_map[f"C_fusion_w{w:.1f}"] = np.zeros(n_samples, dtype=np.float64)

    fold_rows: list[dict[str, float | int | str]] = []

    for fold, (train_idx, valid_idx) in enumerate(logo.split(x_spec, y, groups), start=1):
        x_spec_tr = x_spec[train_idx]
        x_spec_va = x_spec[valid_idx]
        x_emb_tr = x_emb[train_idx]
        x_emb_va = x_emb[valid_idx]
        y_tr = y[train_idx]
        y_va = y[valid_idx]
        holdout_group = int(groups[valid_idx][0])

        pls_model = fit_pls_model(x_spec_tr, y_tr, n_components=PLS_COMPONENTS)
        if pls_model is None:
            y_spec = np.full(len(valid_idx), y_tr.mean(), dtype=np.float64)
            train_scores = np.full((len(train_idx), 1), y_tr.mean(), dtype=np.float64)
            valid_scores = np.full((len(valid_idx), 1), y_tr.mean(), dtype=np.float64)
        else:
            y_spec = pls_model.predict(x_spec_va).ravel().astype(np.float64)
            train_scores = pls_model.transform(x_spec_tr).astype(np.float64)
            valid_scores = pls_model.transform(x_spec_va).astype(np.float64)
        y_species = fit_ridge_predict(x_emb_tr, y_tr, x_emb_va, alpha=RIDGE_ALPHA)

        oof_map["A_spec_only"][valid_idx] = y_spec
        oof_map["B_species_only"][valid_idx] = y_species

        fold_rows.append(
            {
                "pattern": "A_spec_only",
                "fold": fold,
                "holdout_species_number": holdout_group,
                "fold_rmse": rmse(y_va, y_spec),
            }
        )
        fold_rows.append(
            {
                "pattern": "B_species_only",
                "fold": fold,
                "holdout_species_number": holdout_group,
                "fold_rmse": rmse(y_va, y_species),
            }
        )

        for w in FUSION_WEIGHTS:
            name = f"C_fusion_w{w:.1f}"
            y_fusion = w * y_spec + (1.0 - w) * y_species
            oof_map[name][valid_idx] = y_fusion
            fold_rows.append(
                {
                    "pattern": name,
                    "fold": fold,
                    "holdout_species_number": holdout_group,
                    "fold_rmse": rmse(y_va, y_fusion),
                }
            )

        concat_train = np.hstack([train_scores, x_emb_tr])
        model_d = make_pipeline(StandardScaler(), Ridge(alpha=RIDGE_ALPHA))
        model_d.fit(concat_train, y_tr)
        concat_valid = np.hstack([valid_scores, x_emb_va])
        y_concat = model_d.predict(concat_valid).astype(np.float64)
        oof_map["D_concat_pls_scores_emb"][valid_idx] = y_concat
        fold_rows.append(
            {
                "pattern": "D_concat_pls_scores_emb",
                "fold": fold,
                "holdout_species_number": holdout_group,
                "fold_rmse": rmse(y_va, y_concat),
            }
        )

    summary_rows: list[dict[str, float | str]] = []
    for pattern, preds in oof_map.items():
        pattern_fold_rmses = [
            float(row["fold_rmse"]) for row in fold_rows if row["pattern"] == pattern
        ]
        summary_rows.append(
            {
                "pattern": pattern,
                "loso_oof_rmse": rmse(y, preds),
                "fold_mean": float(np.mean(pattern_fold_rmses)),
                "fold_std": float(np.std(pattern_fold_rmses)),
            }
        )

    results_df = pd.DataFrame(summary_rows).sort_values("loso_oof_rmse").reset_index(drop=True)
    oof_df = pd.DataFrame(oof_map)
    fold_df = pd.DataFrame(fold_rows)
    return results_df, oof_df, fold_df


def main() -> None:
    train_df, test_df, species_id_col, species_name_col, target_col, wave_cols = load_data()
    print(f"train_shape={train_df.shape}")
    print(f"test_shape={test_df.shape}")
    print(f"target_col={target_col}")
    print(f"wave_count={len(wave_cols)}")
    print("")

    print_species_catalog(train_df, test_df, species_id_col, species_name_col)

    train_emb, test_emb, embedding_name, embedding_dim = build_species_embeddings(
        train_df=train_df,
        test_df=test_df,
        species_name_col=species_name_col,
    )
    print("[Embedding]")
    print(f"encoder={embedding_name}")
    print(f"train_embedding_shape={train_emb.shape}")
    print(f"test_embedding_shape={test_emb.shape}")
    print(f"embedding_dim={embedding_dim}")
    print("")

    x_raw = train_df[wave_cols].to_numpy(dtype=np.float64)
    x_band2, wn_band2 = select_band2(wave_cols, x_raw)
    x_spec = snv(x_band2)
    y = train_df[target_col].to_numpy(dtype=np.float64)
    groups = train_df[species_id_col].to_numpy()

    print("[Spectral features]")
    print(f"band2_range_cm-1={BAND2_RANGE}")
    print(f"band2_feature_count={x_band2.shape[1]}")
    print(f"band2_min_cm-1={wn_band2.min():.5f}")
    print(f"band2_max_cm-1={wn_band2.max():.5f}")
    print(f"pls_components={PLS_COMPONENTS}")
    print("")

    results_df, oof_df, fold_df = evaluate_models(
        x_spec=x_spec,
        x_emb=train_emb,
        y=y,
        groups=groups,
    )
    results_df.to_csv(RESULTS_PATH, index=False)
    oof_df.to_csv(OOF_PATH, index=False)
    fold_df.to_csv(Path(__file__).resolve().parent / "fold_results.csv", index=False)

    best = results_df.iloc[0]
    print("[LOSO results]")
    print(results_df.to_string(index=False, float_format=lambda v: f"{v:.6f}"))
    print("")

    print("[Best pattern]")
    print(
        f"best_pattern={best['pattern']}, "
        f"loso_oof_rmse={best['loso_oof_rmse']:.6f}, "
        f"fold_mean={best['fold_mean']:.6f}, "
        f"fold_std={best['fold_std']:.6f}"
    )
    if str(best["pattern"]).startswith("C_fusion"):
        print("comment=スペクトル予測と樹種埋め込み予測の補完が効いています。")
    elif str(best["pattern"]).startswith("B_"):
        print("comment=樹種名だけで unseen species の含水率傾向をかなり説明できています。")
    elif str(best["pattern"]).startswith("D_"):
        print("comment=PLS score と樹種埋め込みを同時に使う特徴量結合が最も安定でした。")
    else:
        print("comment=今回の設定ではスペクトル単独が最も強く、樹種埋め込みの追加効果は限定的でした。")
    print("")
    print(f"saved_results={RESULTS_PATH}")
    print(f"saved_oof={OOF_PATH}")
    print(f"saved_fold_results={Path(__file__).resolve().parent / 'fold_results.csv'}")


if __name__ == "__main__":
    main()
