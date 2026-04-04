# ケン・リース - CLAUDE.md

## Goal
このプロジェクトは、ケン・リースとの案件リポジトリである。
目的は、要件整合性・説明責任・納品可能性を保ちながら価値のある成果物を作ること。

## Read First
1. `PROJECT.md`
2. `DATA_CONTRACT.md`
3. `SESSION_NOTES.md`
4. `docs/business_context.md`
5. 直近の `meeting_notes/`

## Principles
- 実装前に目的・利用者・KPI・制約を確認する
- 不明点は `docs/assumptions.md` に残す
- 会議後は `/log-meeting` で議事録を作成し SESSION_NOTES.md も更新する
- `src/` は本命コード、`ai-src/` は試作コード
- 分析結果は意思決定につながる形で残す

## Directory Rules
- `src/` 本命コード
- `ai-src/` AI試作
- `docs/` business_context / data_dictionary / metrics / assumptions
- `deliverables/` クライアント提出物
- `meeting_notes/` 議事録
- `daily_reports/` 日次ログ（hook自動生成）
- `weekly_reports/` 週次ログ（月曜 hook自動生成）
- `monthly_reports/` 月次ログ（1日 hook自動生成）

## Workflow
- `.steering/requirements.md`, `design.md`, `tasklist.md` を起点に進める
- 変更時は理由・影響範囲・懸念点を明示する
- 必要に応じて Codex にレビューを依頼する
