---
name: review-exp
description: 実験コードと設計の妥当性をレビューし、採用可否まで判断する。
---

# Review Experiment

## Mission
実験を、再現性、validation、leakage、実装整合の観点で評価する。

## Review Axes
- requirement との整合
- validation の妥当性
- train と inference の整合
- leakage risk
- seed 固定と再現性
- 設定管理とログ
- baseline との差分理由

## Workflow
1. 目的と改善仮説を確認する。
2. 上の review axes でクリティカルな問題から見る。
3. 必要なら `code-reviewer` にコード面の補助レビューを依頼する。
4. `critical / medium / nice to have` に分ける。
5. `adopt now / fix then adopt / reference only / discard` のどれかを決める。
6. 次実験の仮説を 1 つに絞る。

## Guardrails
- score だけで採用を決めない。
- validation が怪しい改善は採用しない。
- baseline 差分が説明できない実験は評価を下げる。
- nice to have を critical と混ぜない。

## Output
- Summary
- Good points
- Critical issues
- Medium issues
- Nice to have
- Adopt decision
- Recommended next experiment
