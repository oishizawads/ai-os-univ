---
name: work-implementation
description: 業務・社内開発を、目的確認から実装、レビュー、記録まで進める。
---

# Work Implementation

## Mission
仕事用プロジェクトの変更を、目的と制約に沿って安全に実装する。

## Read Context
最初に読む:
- `CLAUDE.md`
- `PROJECT.md`
- `DATA_CONTRACT.md`
- `SESSION_NOTES.md`

必要な範囲だけ読む:
- `docs/`
- `meeting_notes/`
- KPI や運用ルール関連ファイル

## Workflow
1. 目的、やらないこと、成功条件を先に固定する。
2. 必要なら `assumptions.md` に前提を書く。
3. `.steering/requirements.md` `design.md` `tasklist.md` に変更方針を落とす。
4. 実装は最小差分を基本にし、既存運用を壊さない。
5. 変更後はレビュー観点を自分で洗い出す。
6. `SESSION_NOTES.md` に結果と次アクションを残す。

## Optional Parallel Help
必要なときだけ使う:
- `product-analyst`: スコープ整理、KPIとの接続、不要作業の切り分け
- `code-reviewer`: 一般コードレビュー
- `backend-reviewer`: API、インフラ、セキュリティ観点のレビュー

## Guardrails
- 不明点を放置したまま広く実装しない。
- `src/` は本番コード、`ai-src/` は試作コードとして扱う。
- 仕様変更と実装変更を混ぜすぎない。
- 運用影響、依存先、ロールバック観点を残す。
- 変更後はテスト不足、例外処理、設定管理の抜けを最低限確認する。

## Output
- Objective
- Scope
- Deliverables
- Risks
- Change summary
- Next actions
