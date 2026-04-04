---
name: review-exp
description: 実験コードと設計の整合性をレビューし、採否判断まで行う
---

# Review Experiment

## Purpose
この skill は、競技実験に対して「よさそう」ではなく、採用可能かどうかを判定するためのレビューを行う。

## Review Axes
1. 要件との整合性
2. validation の妥当性
3. train / inference の整合性
4. leakage risk
5. seed固定と再現性
6. 設定管理の明確さ
7. ログ・保存物の妥当性
8. 過剰複雑化の有無
9. baselineとの差分の説明可能性
10. 次の改善に繋がる学びが残っているか

## Output Format
- Summary
- Good points
- Critical issues
- Medium issues
- Nice to have
- Adopt decision:
  - Adopt now
  - Fix then adopt
  - Keep as reference only
  - Discard
- Recommended next experiment

## Hard Rules
- スコアだけで褒めない
- validationが怪しい改善は採用しない
- train / inference 不整合は重度扱い
- baselineとの差分が説明できないものは保留寄りに扱う