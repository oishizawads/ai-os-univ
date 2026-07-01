---
title: "振り返りループ（学習を毎回閉じる）"
type: playbook
domain: general
tags: [retrospective, aar, postmortem, weekly-review]
created: 2026-06-18
source:
  title: "US Army AAR / Google SRE Book Ch.15 / Getting Things Done"
  author: "US Army, Google SRE, David Allen"
---

## 原則
やりっぱなしは学習にならない。**低コストで毎回ループを閉じる**仕組みだけ持つ（重い儀式は続かない）。

## 手順
- **AAR 4問（タスク後3分）**: ①何を意図したか ②実際に何が起きたか ③なぜ差が生じたか ④次どうするか。`result.md`・`SESSION_NOTES` に追記。**最小で毎回閉じる主力**。
- **Blameless Postmortem（失敗時 / Google SRE）**: 「誰のせい」でなく「なぜプロセスがそれを許したか」。PoC失敗・分析ミス・炎上後に。書式は `failure_patterns/` へ。
- **インシデント即日記録**: 問題はその日に「何が起きた/判断根拠/結果/次」を残す。鮮度が根本原因分析の精度を決める。
- **週次レビュー（GTD・金曜30分）**: 未完了・新情報・優先順位を棚卸し→翌週の意図を設計。GTDの他は使わなくてもこれだけで回収。

## 判断基準
- 通常タスク → AAR 4問のみ。
- 失敗/想定外 → Blameless Postmortem ＋ failure_patterns 記録。
- 週次 → レビューで WSJF キュー更新（[[decision_triage]]）。

## 失敗例
- 後日まとめて振り返る（記憶が薄れ根本原因を誤る）。
- 失敗を個人の責任で終える（プロセスの穴が残り再発）。
- 重い振り返りテンプレを作って続かない。

関連: [[META_MAP]] ⑧改善層 / [[decision_triage]]。
