---
name: submit-monitor
description: submission 前後の確認と記録更新を漏れなく行う。
---

# Submit Monitor

## Mission
提出前後の確認漏れを防ぎ、CV と public score の差分を記録する。

## Before Submit
- format を確認する
- inference の整合を確認する
- experiment id を確定する
- `result.md` を更新する
- submission filename を確認する

## After Submit
- public score を記録する
- local CV との差分を確認する
- 良化、悪化、想定外を切り分ける
- `SESSION_NOTES.md` を更新する

## Guardrails
- experiment id なしで出さない。
- 提出ファイル名と中身の対応を残す。
- score 差分の解釈を 1 行でも残す。

## Output
- Submission status
- Risks
- Record checklist
