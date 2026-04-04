---
title: "ML Terms Glossary"
type: glossary
domain: ds
tags: [glossary, ml, cv, oof, validation]
created: 2026-04-05
---

## Summary
このOSで使うML用語の定義。AIへの指示で意味がブレないようにする。

---

## CV（Cross-Validation）
データを複数のfoldに分割し、モデルの汎化性能を推定する手法。
このOSでは **CVスコアの改善が再現性を持つこと** を Solid 実験の条件とする。
Public LBではなく CV を意思決定の主軸にする。

## OOF（Out-of-Fold prediction）
CV中、各サンプルが validation fold にいたときの予測値を集めたもの。
全trainデータに対して1つの予測ベクトルが得られる。
アンサンブルの重み付けや最終スコア確認に使う。

## LOSO（Leave-One-Species-Out）
near-infrared-challenge 固有のCV設計。
樹種（species）単位で1グループをholdoutする GroupKFold の変種。
樹種間のドメインシフトを評価するために採用。

## Solid戦略
CV改善が再現性を持ち、実装がシンプルで追試できる改善案。
ベースラインとして保持し続ける実験群。

## Explosive戦略
失敗してもSolidなスコアを損なわないが、成功時のアップサイドが大きい実験。
先行研究や上位解法で有効性が示唆されているものを選ぶ。

## Leakage（データリーク）
学習データに test の情報が混入すること。
または target の情報が特徴量に混入すること。
CVスコアが高いのに Public LB が低い場合の主要原因の1つ。

## Steering
実験・タスク前に作る設計書セット。
`requirements.md` / `design.md` / `tasklist.md` の3点セット。
`.steering/YYYY-MM-DD-expXXX-name/` に配置する。

## SESSION_NOTES
セッションをまたいで引き継ぐ作業メモ。
現在の焦点・進捗・次アクションを記録する。
セッション終了前に必ず更新する。

## DECISION_LOG
重要な技術的・設計的意思決定の記録。
「なぜそうしたか」が後から分かるようにする。
フォーマット: `## YYYY-MM-DD | タイトル`

## src / ai-src
- `src/`: 本命コード（動作確認済み・整理済み）
- `ai-src/`: AIによる試作・叩き台（品質保証なし）

## Experiment ID prefix
- `expA`: Claude主導の実験
- `exp2`: 人間主導の実験
