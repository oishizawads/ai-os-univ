# AI OS SESSION_NOTES

## Current Focus
- workspace 全体の運用基盤として ai-os を機能させる
- コンペ・実務の両方で共通のコマンド・スキル・エージェントを使えるようにする

## What Exists
- `C:/workspace/.claude/` に commands / skills を配置済み（全プロジェクトから使用可）
- `~/.claude/agents/` に 10 エージェント（researcher, experiment-planner, meeting-note-writer 含む）
- SessionEnd hooks 有効化済み（daily/weekly/monthly 自動生成）
- competition / client プロジェクト雛形テンプレ
- steering テンプレ（requirements / design / tasklist）
- report テンプレ（daily / weekly / monthly / meeting_note）
- コマンド: baseline / eda / review-exp / work-review / log-meeting / weekly-review / monthly-review / new-project
- スキル: experiment-workflow / work-implementation / bug-investigation / review-exp / meeting-log 他

## Active Projects
- `competitions/near-infrared-challenge/` ← NIR→含水率予測、LOSO RMSE ベスト 20.17
- `work/zetax/` ← ZetaX 社内OS
- `work/clients/jbr/` ← JBR 案件
- `work/clients/ケン・リース/` ← 構造作成済み、中身は外部ドキュメントから移行予定

## What Is Missing
- ケン・リース PROJECT.md / SESSION_NOTES.md の中身（スマホ同期後に移行）

## Decisions
- `src/` は本命、`ai-src/` はAI試作
- 競技: CV再現性優先、LOSO を主軸
- 業務: 要件整合性・説明責任優先
- Claude = PM、Codex = Engineer
- hooks は C:/workspace/.claude/settings.json で管理

## Next Actions
1. ケン・リース の情報を外部ドキュメントから PROJECT.md / SESSION_NOTES.md に移行
2. suggest-claude-md-hook の動作確認
3. コンペ: LocalPLS / SLM埋め込み実験を再開
---
## Session Log 2026-04-01 23:51

**編集ファイル:**
- .claude\settings.json
- ai-os\.claude\skills\slides-maker\SKILL.md
- ai-os\hooks\lib\rotate_daily_report.py
- ai-os\hooks\lib\session_notes_sync.py
- ai-os\hooks\rotate-daily-report-hook.sh
- ai-os\hooks\suggest-claude-md-hook.sh
- ai-os\hooks\sync-session-notes-hook.sh
