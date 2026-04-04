---
title: "Experiment Log Standard"
type: standard
domain: ds
tags: [experiment, logging, reproducibility, standard]
created: 2026-04-05
---

## Summary
実験記録の最低記載項目。コンペ・実務PoC共通。
「再現できない実験は価値が低い」原則を運用で担保する。

## 最低記載項目（result.md）

```markdown
## Experiment ID
expA001_baseline  # prefix: A=Claude主導 / 2=人間主導

## Objective
この実験で何を確かめるか（1文）

## Validation
使ったCV手法と設定（例: GroupKFold(n_splits=5, groups=species_number)）

## Seed
42  # 固定すること

## Model / Preprocessing
モデル名(主要パラメータ) / 前処理の概要

## Fold Scores
- Fold 1: XX.XX
- Fold 2: XX.XX
...

## Mean / Std
- Mean: XX.XX
- Std: XX.XX
- OOF Score: XX.XX  # コンペの場合

## Findings
- 何がわかったか（観察事実）

## Failure Modes
- 何がうまくいかなかったか

## Next Hypothesis
この結果を踏まえて次に試すこと
```

## Solidな実験の条件
- CVスコアの改善が再現性を持つ（seed固定・fold間ばらつき許容範囲内）
- 実装がシンプルで追試できる
- Public LBとCVの順位相関がある（コンペの場合）

## やってはいけないこと
- seedを変えながらスコアを選ぶ
- Fold Scoresを記録せずにMeanだけ書く
- Findingsを「良かった」だけで終わらせる
- 失敗した実験の記録を消す

## ファイル配置
```
experiments/
  expA001_baseline/
    notes.md    ← 実験前に書く（目的・仮説）
    result.md   ← 実験後に書く（結果・考察）
```
