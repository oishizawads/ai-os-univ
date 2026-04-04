# METRIC.md

## Metric Name
RMSE

## Definition
予測値と正解値の二乗誤差平均平方根。小さいほど良い。

## Better Direction
Lower is better

## What Counts as Meaningful Improvement
- mean 改善だけでなく std の悪化も見る
- ほんのわずかな改善は validation の揺れかもしれない
- 複雑化したのに improvement が小さい場合は慎重に扱う

## Comparison Rules
- 同一 validation 条件で比較する
- mean / std / fold breakdown をセットで見る
- public LB だけ良い案は採用しない