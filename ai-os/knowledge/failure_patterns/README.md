# Failure Patterns

実際に経験した失敗パターンをここに記録する。
作り話・一般論は書かない。実際の案件・コンペ・実装で起きたことだけ。

## 現在のエントリ

| ファイル | 対象 | 収録パターン数 |
|---|---|---|
| [cv_design_mistakes.md](cv_design_mistakes.md) | CV設計の失敗 | 4 |
| [data_leakage_patterns.md](data_leakage_patterns.md) | データリークパターン | 5 |
| [requirement_failures.md](requirement_failures.md) | 要件・スコープ管理の失敗 | 5 |
| [model_training_failures.md](model_training_failures.md) | モデル学習の失敗 | 5 |

## フォーマット

```markdown
---
title: "失敗の名前"
type: failure_pattern
domain: ds | ml | pm | coding | general
tags: []
created: YYYY-MM-DD
project: ""  # どの案件・コンペで起きたか（任意）
---

## パターン名

**何が起きたか**: （具体的に）

**根本原因**: （なぜ起きたか）

**検知方法**: （どうすれば早期発見できるか）

**対処**: （起きたときの対応）

**再発防止**: （次回に向けてのチェック項目）
```

---

失敗が起きたらここに追記する。
