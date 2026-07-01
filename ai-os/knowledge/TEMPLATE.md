# Knowledge File Template

新しい知識ファイルを作るときはこのフォーマットを使う。
「原則・判断基準・手順・失敗例」に圧縮してから保存する。rawメモをそのまま保存しない。

---

## ファイル命名規則（必須）

```
{概念名}_{元本略称}.md
```

- **概念名**: 解決する課題・判断基準・フレームワーク名（英語、スネークケース）
- **元本略称**: 出典本の短い識別子（英語、スネークケース）

### 例

| 元本 | 概念 | ファイル名 |
|------|------|-----------|
| Clean Code | Meaningful Names | `meaningful_names_clean_code.md` |
| Atomic Habits | Identity-Based Habits | `identity_habits_atomic.md` |
| Inspired | Product Discovery | `product_discovery_inspired.md` |
| Team Topologies | Stream-Aligned Teams | `stream_aligned_teams_tt.md` |

---

```markdown
---
title: ""
type: principle | playbook | framework | failure_pattern | eval_rule
domain: ds | ml | pm | rag | coding | business | general | self_dev
tags: []
created: YYYY-MM-DD
source:
  title: ""       # 元本の正式タイトル
  author: ""      # 著者名
  isbn: ""        # ISBN（あれば）
  chapter: ""     # 関連章（あれば）
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
| framework | `knowledge/frameworks/` または `knowledge/business_frameworks/` |
| failure_pattern | `knowledge/failure_patterns/` |
| eval_rule | `knowledge/evals/` |
| 用語定義 | `knowledge/glossaries/` |

### frameworks/ vs business_frameworks/ の使い分け

- `frameworks/`: **技術系・エンジニアリング系**のフレームワーク（設計思想、アーキテクチャ、データサイエンス手法）
- `business_frameworks/`: **ビジネス・PM・自己啓発系**のフレームワーク（マネジメント、組織、戦略、生産性）

既存の `frameworks/` 内に混在しているビジネス・自己啓発本は、今後の改修時に `business_frameworks/` へ移行する方針。
