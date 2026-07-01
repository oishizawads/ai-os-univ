---
name: viz-style
description: 可視化の既定ルール。subplots+constrained_layout、日本語フォント、棒グラフ y軸0起点、jet/rainbow 禁止。
---

# Visualization Style

## Mission
読めて・誤解させない図を、毎回同じ品質で出す。matplotlib/seaborn を使う全タスクで適用する。

## Rules
- `fig, ax = plt.subplots(figsize=..., constrained_layout=True)` 形式を使う。`plt.figure()`+ステートフルAPIは使わない。
- 日本語が出るデータは日本語フォントを設定（`japanize_matplotlib` import 等）。文字化けを残さない。
- フォントは読めるサイズに（`font_scale` や `figsize` で調整）。潰れたラベルを放置しない。
- 棒グラフ（量の比較）は **y軸を0起点**にする。差を誇張する切り詰めをしない。
- カラーマップに `jet` / `rainbow` を使わない。連続量は `viridis` 等の知覚均等系、カテゴリは `muted` 等。
- 軸ラベル・単位・凡例・タイトルを付ける。出所/集計条件が必要なら caption に。

## Recommended setup
```python
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib  # 日本語ラベルがある場合

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.2)
fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
```

## Guardrails
- 「とりあえず描画」で軸ラベルなしの図を出さない。
- 棒グラフの y軸切り詰めで差を演出しない。
- 文字化け（□□□）のまま提出・保存しない。
- 図を保存するときの出力パスは [[path-io]] に従う。
