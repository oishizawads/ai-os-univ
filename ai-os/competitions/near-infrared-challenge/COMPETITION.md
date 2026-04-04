# COMPETITION.md

## Competition
Near Infrared Spectral Analysis Challenge

## Task
木材の近赤外スペクトルから含水率を予測する回帰タスク。

## Metric
RMSE

## Submission Format
- test データ各行に対する予測値を提出
- id と prediction の整合を必ず確認する
- 並び順や件数不整合を起こさない

## Constraints
- leakage 禁止
- validation を雑にしない
- public LB のみで判断しない
- 再現できない改善は採用しない

## Timeline
- 本番期間中は、実験ログと submission ログを必ず残す

## Notes
- この課題では前処理と validation 設計が特に重要
- スコアだけでなく、筋の良さと再現性を優先する