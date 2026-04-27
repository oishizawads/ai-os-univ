# AI OS - CLAUDE.md

## Purpose
このディレクトリは、Claude Code を用いた開発・分析・実験・業務遂行のための共通AI運用OSである。
目的は、案件とコンペを同じ思想・同じ手順・同じ品質基準で回せるようにすること。

## Core Principles
- いきなり実装に入らない。まず要件・設計・タスク分解を行う
- セッションを跨ぐ知識は、会話に依存せずファイルに残す
- 再現できない実験・説明できない変更・追跡できない意思決定は価値が低い
- AIは便利な代筆装置ではなく、運用プロセスに組み込む
- コンペではCVの再現性を最優先
- 業務では要件整合性・説明責任・納品可能性を最優先
- `src/` は本命コード、`ai-src/` はAIの試作・叩き台とする

## Standard Workflow
1. `python C:/workspace/ai-os/hooks/lib/session_start.py [project_dir]` でコンテキストロード
2. 対象プロジェクトの `CLAUDE.md` を読む
3. 知識ベース `/path/to/your/obsidian-vault/raw/_INDEX.md` の概要を把握する
4. 関連する `knowledge/` を確認する（principles/ frameworks/ playbooks/ failure_patterns/）
5. 目的、制約、成功条件を要約する
6. 実装・分析・実験を行う（並列エージェント戦略: `knowledge/playbooks/parallel_agent_workflow.md` 参照）
7. 結果を記録する（実験は result.md → auto-ledger が experiment_ledger.csv に自動追記）
8. `SESSION_NOTES.md` を更新する
9. 重要な意思決定は `ai-os/decisions/YYYY-MM.md` に記録する（プロジェクト横断）
10. プロジェクト固有の失敗は `knowledge/failure_patterns/` に記録する

## Knowledge Resources
- `/path/to/your/obsidian-vault/raw/_INDEX.md` — 知識ベースの目次
- `knowledge/principles/` — 長期不変の思考原則
- `knowledge/frameworks/` — 思考の足場
- `knowledge/playbooks/` — 業務別標準手順（parallel_agent_workflow.md 含む）
- `knowledge/failure_patterns/` — 実際に起きた失敗パターン
- `decisions/YYYY-MM.md` — 横断的意思決定ログ（月別）
- `EVAL_POLICY.md` — 評価基準
- `WORKFLOW_SPEC.md` — AI運用設計の全体像

## Hooks（自動実行）
| タイミング | 処理 |
|-----------|------|
| PreToolUse (Bash) | `guard_dangerous_commands.py` — 危険コマンドをブロック |
| PostToolUse (Edit/Write) | `suggest_claude_md.py` — CLAUDE.md 更新提案 |
| PostToolUse (Edit/Write) | `auto_ledger.py` — result.md 書き込み時に experiment_ledger.csv 自動追記 |
| SessionEnd | `rotate_daily_report.py` — 日次/週次/月次レポート生成 |
| SessionEnd | `session_notes_sync.py` — 編集ファイルをSESSION_NOTESに記録 |

## Global Rules
- 実装や分析の前に、前提・制約・評価基準を明文化する
- 推測で進める場合は、推測であることを明示する
- 変更時は「何を」「なぜ」「どこまで」変えたかを説明する
- 危険な変更、破壊的変更、大規模置換は明示的に扱う
- 空のファイルを放置しない。使うものから埋める
- 反復タスクは skill / command に落とし込む
- セッション終了前に学びを `SESSION_NOTES.md` に残す

## When Working on Competitions
- CVの妥当性、リーク、OOFの解釈、推論整合性を優先して確認する
- public LBだけで案を採用しない
- solid strategy と explosive strategy を分けて考える
- 実験前に `.steering/requirements.md`, `design.md`, `tasklist.md` を作る
- 実験後は `result.md` を更新する
- 探索・PoC局面では `knowledge/playbooks/vibe_coding.md` のワークフローを適用してよい（高速ループ優先、記録より速度）

## When Working on Client Projects
- 要件定義、前提、データ契約、意思決定ログを重視する
- 不明点は `assumptions.md` や `PROJECT.md` に記録する
- 会議後は `meeting_notes/` と `SESSION_NOTES.md` を更新する
- 実装より前に、成果物・利用者・KPI・制約を確認する

## Review Policy
- 実装後はレビューを行う
- 競技コードは `review-exp`
- 業務コードは `work-review`
- エラー発生時は `error-analyzer` 観点で最低3仮説出す
- 必要に応じて Codex に差分レビューや横断確認を依頼する
- Vibe Coding的ループでは Claude Code と GitHub Copilot のクロスレビューを推奨（`knowledge/playbooks/vibe_coding.md` 参照）

## Output Style
- まず結論
- 次に理由
- 次にリスク
- 最後に次アクション
- 冗長な一般論より、すぐ使える具体案を優先する