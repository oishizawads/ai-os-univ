# Competition Project - CLAUDE.md

## Goal
このプロジェクトはコンペ用の実験管理リポジトリである。
目的は、CV再現性を保ちながら、筋の良い改善を積み上げること。

## Principles
- CVが不安定な案は本命にしない
- 再現できない実験は価値が低い
- public LBだけで判断しない
- 前処理とvalidationを先に詰める
- いきなり複雑化しない
- baselineとの差分で改善を判断する
- solid strategy と explosive strategy を分けて考える

## Read First
1. `COMPETITION.md`
2. `DATASET.md`
3. `METRIC.md`
4. `SESSION_NOTES.md`
5. `VALIDATION_RULES.md`

## Directory Rules
- `src/` は本命コード
- `ai-src/` はAI試作
- `experiments/expAxxx_*` はClaude主導
- `experiments/exp2xx_*` は人間主導
- `daily_reports/` 日次ログ（hook自動生成）
- `weekly_reports/` 週次ログ（毎週月曜 hook自動生成）
- `monthly_reports/` 月次ログ（毎月1日 hook自動生成）
- `meeting_notes/` ミーティング議事録

## Experiment Rules
- 実験前に `.steering/` を作る
- `requirements.md`, `design.md`, `tasklist.md` を前提に進める
- 実験後は `notes.md`, `result.md`, `SESSION_NOTES.md` を更新する
- train / inference の整合を崩さない
- seed と validation を明記する

## Review Rules
- 実装後は `review-exp` 観点で見直す
- リーク、推論不整合、seed漏れ、設定散乱を重点確認する