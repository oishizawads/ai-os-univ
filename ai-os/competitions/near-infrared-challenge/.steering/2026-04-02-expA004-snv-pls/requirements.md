# requirements.md

## Objective
SNV前処理 + PLSRegression + GroupKFold で、未知樹種への汎化性能を検証する。

## Background
- expA003でPLS+KFoldはGroupKFold OOFが爆発（n=20で119）→ PLSが樹種固有パターンを学習していた
- SNVは各サンプルのスペクトルを自身の平均・標準偏差で正規化 → 樹種間スケール差を除去
- SNVによりPLSが「含水率に関係する成分」だけを学べるようになることを期待
- CVはGroupKFold(5)で未知樹種への汎化を正直に評価する
- 目標: GroupKFold OOF でRidgeraw(42.44)を下回ること

## Success Criteria
- SNV + PLS の GroupKFold OOF が 42.44 を下回る
- n_componentsのスイープで安定した候補が見つかる（fold std が小さい）
- 提出ファイルが生成される

## Constraints
- CV: GroupKFold(5, groups=species_number) — 正直な評価のため
- SNVはサンプル内完結処理なのでleakなし（fold外でfitする必要なし）
- train/inference で同じSNV処理を使う
