# DATASET.md

## Target
含水率

## IDs
- sample number などの識別列がある場合は、学習特徴量に直接混入させない
- 並び順依存に注意する

## Main Columns
- sample number
- species number
- 樹種
- 含水率
- 多数の波数列

## Missing / Noise Concerns
- 計測ノイズ
- 前処理前のスペクトル揺れ
- 樹種や測定条件に起因する構造差

## Leakage Concerns
- target と強く紐づく派生列の混入
- split 設計が不適切な場合の見せかけ改善
- preprocessing の fit/transform 不整合

## Preprocessing Cautions
- raw / SNV / SG / derivative は必ず baseline と比較する
- 前処理を fold 外で fit しない
- train / inference で同じ処理を使う