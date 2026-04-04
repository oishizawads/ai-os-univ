# Client Project - CLAUDE.md

## Goal
このプロジェクトは、業務課題に対する分析・PoC・実装支援を進める案件リポジトリである。
目的は、要件整合性・説明責任・実装可能性を保ちながら価値のある成果物を作ること。

## Read First
1. `PROJECT.md`
2. `DATA_CONTRACT.md`
3. `SESSION_NOTES.md`
4. `docs/business_context.md`
5. `docs/metrics.md`

## Principles
- 実装前に目的、利用者、KPI、制約を確認する
- 不明点は `docs/assumptions.md` に残す前提で扱う
- `src/` は本命コード、`ai-src/` は試作コード
- 会議後は `/log-meeting` で議事録を作成し `SESSION_NOTES.md` も更新する
- 分析結果は意思決定につながる形で残す
- 技術的に可能でも、業務価値が薄いものは優先しない

## Workflow
- `.steering/requirements.md`, `design.md`, `tasklist.md` を起点に進める
- 変更時は、理由・影響範囲・懸念点を明示する
- 必要に応じて Codex にレビューを依頼する
- レポート・分析・コードを混ぜずに整理する