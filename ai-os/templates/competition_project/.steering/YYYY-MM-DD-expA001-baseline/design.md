# design.md

## Hypothesis
まずはシンプルな baseline を作り、そこから前処理・validation の改善余地を評価する方が良い。

## Approach
- 最小限の特徴量・モデルで baseline を構築
- validation を固定
- train / inference の共通処理を明示

## Files to Change
- experiments/expA001_baseline/train.py
- experiments/expA001_baseline/inference.py
- experiments/expA001_baseline/settings.py

## Risks
- baseline なのに複雑になる
- validation が曖昧なままになる
- 推論整合が崩れる

## Acceptance Criteria
- 実行可能
- 再現可能
- result.md を書ける