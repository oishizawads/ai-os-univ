---
argument-hint: [target-analysis-or-file]
description: Run a structured causal inference review on a task or artifact.
---

# causal-check

## Objective
因果推論タスクの識別戦略・推定・診断・感度分析を構造化してレビューする。

## When to Use
- 施策効果や機能変更の影響を推定しようとしている
- 観察データで因果を主張したい
- 推定方針が不安で、識別戦略から見直したい
- 結果をレビューして因果解釈が妥当か確認したい

## Workflow
1. Load skill `causal-inference`.
2. Read project context (`CLAUDE.md`, `SESSION_NOTES.md`, relevant data docs).
3. Ask or infer the estimand: treatment `T`, outcome `Y`, population, ATE/ATT/CATE/LATE.
4. List candidate identification strategies and pick the strongest given the data.
5. List required diagnostics for that strategy.
6. Confirm estimation approach and packages.
7. Plan sensitivity / robustness checks.
8. If uncertainty is high, route to `decision-lab` for multi-path analysis.
9. Summarize review in the output format.

## Output Format

### Estimand
-

### Identification
- Strategy
- Assumptions
- Threats

### Data Diagnostics
-

### Estimation Plan
-

### Sensitivity Plan
-

### Risks
-

### Decision-lab Needed?
- Yes / No / Maybe

### Next Action
1.
2.
3.

## Guardrails
- Do not skip assumption listing.
- If no plausible identification strategy exists, say so explicitly.
- Prefer `decision-lab` when assumptions are contestable.
- Do not present correlation as causation.
