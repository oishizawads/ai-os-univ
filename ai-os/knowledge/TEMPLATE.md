# Knowledge File Template

新しい知識ファイルを作るときはこのフォーマットを使う。
「原則・判断基準・手順・失敗例」に圧縮してから保存する。rawメモをそのまま保存しない。

---

```markdown
---
title: ""
type: principle | playbook | framework | failure_pattern | eval_rule
domain: ds | ml | pm | rag | coding | general
tags: []
created: YYYY-MM-DD
source: ""  # 本・論文・実務経験など
---

## Summary
（3〜5行で要点。これだけ読めば何の知識かわかる）

## Core Principles
- 原則1
- 原則2

## Decision Rules
- どういう基準で判断するか
- 適用条件（これが当てはまるときに使う）
- 非適用条件（これが当てはまるときは使わない）

## Procedure
1. 手順1
2. 手順2
3. 手順3

## Anti-patterns
- やりがちな失敗1（なぜ失敗か）
- やりがちな失敗2

## Example
（良い適用例を1つ）

## Eval
- この知識が正しく使われたかのチェック項目1
- チェック項目2
```

---

## 保存先の選び方

| type | 保存先 |
|------|--------|
| principle | `knowledge/principles/` |
| playbook | `knowledge/playbooks/` |
| framework | `knowledge/frameworks/` |
| failure_pattern | `knowledge/failure_patterns/` |
| eval_rule | `knowledge/evals/` |
| 用語定義 | `knowledge/glossaries/` |
