# AI OS - CLAUDE.md

## Purpose
このディレクトリは、Claude Code を用いた開発・分析・実験・業務遂行のための共通AI運用OSである。
目的は、案件とコンペを同じ思想・同じ手順・同じ品質基準で回せるようにすること。

## エージェントロール分担

| エージェント | 役割 | 起動方法 |
|------------|------|---------|
| **Claude Code** | PM＆既定の実行者（設計・判断・実装・レビュー・統合） | — |
| **OpenCode Go** | 高効率エンジニア（実装・高速コーディング）※委譲時 | `python C:/workspace/tools/opencode_coder.py "<prompt>"` |
| **Codex** | read-only レビュー・診断（⚠️要節約）※委譲時 | `python C:/workspace/tools/codex_coder.py "<prompt>"` |
| **Gemini** | 実装セカンドオピニオン・リサーチ※委譲時 | `python C:/workspace/tools/gemini_coder.py "<prompt>"` |
| **decision-lab** | 不確実性の高い分析（並列仮説検証） | `C:/workspace/decision-lab/` 参照 |

### 実モデル（正典は root `CLAUDE.md`）
- Claude Code: 現在設定されている Claude Code モデル（再陳腐化を避けるため固定値はここに書かない。root `CLAUDE.md` 参照）
- OpenCode Go: qwen3.6-plus
- Codex: gpt-5.4 (reasoning medium)
- Gemini: gemini-2.5-flash / gemini-3

### コーダールーティング基準
- 既定は Claude 直接実行。委譲は任意の escape hatch（ユーザー指定 or 量産・並列・トークン実利がある時）。
- 高効率・高速実装の委譲 → `python C:/workspace/tools/opencode_coder.py`
- 実装セカンド・リサーチの委譲 → `python C:/workspace/tools/gemini_coder.py`
- read-only レビュー・診断の委譲 → `python C:/workspace/tools/codex_coder.py`（⚠️要節約）
- 分析・予測・因果推論 → `decision-lab`
- 設計・レビュー・最終判断 → Claude Code（自分）

## Token最適化（RTK・任意）
RTK は**任意・非必須**。既定フローには含めない（実測削減 ~0.7%、auto-rewrite フックなし、`rtk` は PATH 未登録）。
ad-hoc に使う場合のみ `C:/workspace/bin/rtk.exe <command>`（例: `rtk.exe gain`）。詳細: `ai-os/shared/standards/rtk_guidelines.md`。

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
7. 結果を記録する（メトリクス追跡は WandB、実験の意図・採用判断・次仮説は result.md に書き残す）
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

| タイミング | 処理 | Status |
|-----------|------|--------|
| PreToolUse (Bash) | `guard_dangerous_commands.py` — 危険コマンドをブロック | ✅ Active |
| PostToolUse (Edit/Write) | `suggest_claude_md.py` — CLAUDE.md 更新提案 | ✅ Active |
| SessionEnd | `rotate_daily_report.py` — 日次/週次/月次レポート生成 | ✅ Active |
| SessionEnd | `session_notes_sync.py` — 編集ファイルをSESSION_NOTESに記録 | ✅ Active |

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

## AI Task Delegation
> **注: ai-delegate（LangGraph 自動オーケストレーター）は 2026-06-21 に撤去済み（コード削除・退避済み）。** 委譲は直接コマンド（`/opencode-coder` / `/gemini-coder` / `/codex-coder` ＝ `tools/*_coder.py` ラッパー）と `/codex:rescue` のみ。`/route`・`/dispatch`・自動ルーティングは廃止。

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
- 必要に応じて Codex / Gemini に差分レビューや横断確認を依頼する
- Vibe Coding的ループでは Claude Code と Codex/Gemini のクロスレビューを推奨（`knowledge/playbooks/vibe_coding.md` 参照）

## Output Style
- まず結論
- 次に理由
- 次にリスク
- 最後に次アクション
- 冗長な一般論より、すぐ使える具体案を優先する