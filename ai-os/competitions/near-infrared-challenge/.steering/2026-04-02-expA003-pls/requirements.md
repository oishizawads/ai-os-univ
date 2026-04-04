# requirements.md

## Objective
RidgeからPLS回帰に変更して、NIRスペクトルの共変動構造を活かした改善を検証する。

## Background
- expA002 KFold OOF=18.62 がbaseline
- PLSはNIR分析の業界標準。1555列の相関構造を潜在成分に圧縮して回帰する
- n_componentsが唯一の主要ハイパーパラメータ。過少=情報損失、過多=過学習
- 前処理はrawのまま（モデル変更の効果を単離する）

## Success Criteria
- n_componentsのスイープ結果が得られる
- best n_componentsでのKFold OOF RMSEがexpA002(18.62)より改善している
- 提出ファイルが生成される

## Constraints
- CV: KFold(5, shuffle=True, seed=42)（expA002と同じ）
- Preprocessing: raw（変更なし）
- leakage禁止・train/inference整合
