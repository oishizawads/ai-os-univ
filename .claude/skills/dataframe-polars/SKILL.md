---
name: dataframe-polars
description: 表データは polars を既定で推奨（pandas は条件付き許容）。LazyFrame で効率化。新規前処理は polars、Kaggle/納品は pandas 可。
---

# DataFrame with Polars

## Mission
表データ処理を、速くて壊れにくい既定（polars）に寄せつつ、現場の制約（Kaggle/納品）では pandas も許容する。**強制ではなく推奨**。

## 使い分け（ハイブルド方針）
- **polars を推奨**: 自分の新規前処理・中間処理・大きめデータ・パイプライン部品。
- **pandas を許容**: 以下に該当するときは無理に移行しない。
  - Kaggle の公開Notebook/カーネルを土台にする
  - クライアント納品物が pandas / scikit-learn 等 pandas前提のエコシステムを要求
  - 既存コードが pandas で、部分改修のコストが利得を上回る
- 1プロジェクト内で**無秩序に混在させない**。境界（読み込み層など）でどちらかに寄せる。

## polars の指針
- 重い処理は `LazyFrame`（`pl.scan_*` → 変換 → `.collect()`）で最適化に任せる。
- I/O は parquet を優先（`scan_parquet` / `write_parquet`）。パスは [[path-io]] に従う。
- join 後は行数を確認（[[sql-analysis]] と同じ精神。意図しない増殖を検知）。
- pandas が必要な外部APIへ渡すときだけ `.to_pandas()` で境界変換する。

## Guardrails
- 「polarsが正義」で Kaggle/納品の現実を壊さない。推奨は推奨。
- polars/pandas をファイルごとに気分で混ぜない。境界を決める。
- LazyFrame の `.collect()` 忘れ（未評価のまま使う）に注意。
- データ層の不変性は [[safe-data-handling]] に従う。
