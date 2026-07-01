---
name: bug-investigation
description: エラーや不具合の原因候補を整理し、最短の切り分け順を出す。
---

# Bug Investigation

## Mission
症状から仮説を立て、最短で原因に到達するための調査順を決める。

## Workflow
1. Symptom を 1 から 3 行で要約する。
2. 再現条件、直前変更、影響範囲を確認する。
3. 仮説を最大 3 つに絞る。
4. 依存、設定、入力、環境、本体コードの順で切り分ける。
5. 必要なら `error-analyzer` に補助調査を依頼する。
6. 最速の triage order を決める。
7. 再発防止策を 1 行で残す。

## Guardrails
- 仮説を増やしすぎない。
- 再現条件を曖昧にしたまま深掘りしない。
- 直前変更と環境差分を最初に確認する。
- 症状、原因、恒久対策を混同しない。

## Output
- Symptom summary
- Hypothesis 1
- Hypothesis 2
- Hypothesis 3
- Fastest triage order
- Prevention
