---
name: python-style
description: Python コードの既定スタイル。公開関数に型ヒント、Google スタイル docstring、インラインコメントは日本語。
---

# Python Style

## Mission
読めて・後から直せる Python を一貫した形で書く。Python を書く全タスクで適用する。

## Rules
- 公開関数・メソッドには**型ヒント**を付ける（引数と戻り値）。
- 公開関数・クラスには **Google スタイル docstring**（Args / Returns / Raises）を書く。
- インラインコメントは**日本語**で、何をやっているかでなく「なぜ」を書く。
- 関数は単一責務・短く。深いネストより早期 return。
- マジックナンバー/文字列は定数化。設定値は処理の奥に埋めない。

## Recommended pattern
```python
def split_by_date(df: pl.DataFrame, cutoff: date) -> tuple[pl.DataFrame, pl.DataFrame]:
    """日付で学習用と検証用に分割する。

    Args:
        df: 分割対象。`date` 列を持つこと。
        cutoff: この日より前を学習、以降を検証に回す。

    Returns:
        (train, valid) のタプル。
    """
    # 時系列リークを避けるため日付で厳密に区切る
    train = df.filter(pl.col("date") < cutoff)
    valid = df.filter(pl.col("date") >= cutoff)
    return train, valid
```

## Guardrails
- 型ヒントなしの公開関数を増やさない。
- docstring に「何を」だけ書いて「なぜ/前提」を落とさない。
- コメントでコードの逐語訳をしない。意図・制約・リークリスクを残す。
