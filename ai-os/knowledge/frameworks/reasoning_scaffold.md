---
title: "Reasoning Scaffold"
type: framework
domain: general
tags: [reasoning, scaffold, structured_thinking]
created: 2026-04-05
---

## Summary
Claudeに自由作文させず、思考の足場を固定する汎用テンプレート。
タスクの種類に応じてセクションを取捨選択して使う。

## 汎用Reasoning Scaffold

```markdown
## Goal
この依頼の最終成果を1文で定義せよ

## Constraints
制約条件を列挙せよ（時間・データ・技術・組織・コスト）

## Context
このタスクに関係する文脈を要約せよ（背景・現状・過去の試み）

## Issue
本質的なイシューを最大3つに絞れ

## Hypotheses
各イシューについて仮説を1〜3個書け

## Options
取りうる選択肢を列挙し、メリデメを比較せよ

## Recommendation
最適案を選び、理由を書け

## Risks
主要リスクと失敗条件を明記せよ

## Next Actions
次に何をするかを3〜5個で出せ（担当・期限付きで）
```

## タスク別バリエーション

### 分析・EDA用
Goal / Constraints / Data Assumptions / Baseline / EDA Plan / Metrics / Risks / Recommendation

### 実装設計用
Goal / Constraints / Architecture / Interfaces / Data Flow / Failure Conditions / Test Points

### 提案・PM用
Business Issue / Target KPI / Proposal / Implementation Steps / Risks / Expected Impact

### 調査・リサーチ用
Research Question / Scope / Key Sources / Comparison Axes / Consensus Points / Gaps / Recommendation

## Eval
- Goalが1文で書けているか
- Constraintsが具体的か（「難しい」ではなく「〇〇がない」）
- Recommendationに根拠があるか
- Next Actionsが実行可能な粒度か
