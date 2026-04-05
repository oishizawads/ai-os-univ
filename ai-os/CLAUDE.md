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
1. 対象プロジェクトの `CLAUDE.md` を読む
2. `SESSION_NOTES.md` を読む
3. 直近の `.steering/` を確認する
4. `/path/to/your/obsidian-vault/raw/_INDEX.md` を読んで知識ベースの概要を把握する
5. 関連する `knowledge/` ファイルを確認する（principles/ frameworks/ playbooks/ failure_patterns/）
6. 目的、制約、成功条件を要約する
7. 実装・分析・実験を行う
8. 結果を記録する
9. `SESSION_NOTES.md` と関連ドキュメントを更新する
10. 失敗・重要判断は `DECISION_LOG.md` または `knowledge/failure_patterns/` に記録する

## Knowledge Resources
- `/path/to/your/obsidian-vault/raw/_INDEX.md` — 知識ベースの目次（何が入っているか）。セッション開始時に読む
- `knowledge/principles/` — 長期不変の思考原則（issue_driven, hypothesis等）
- `knowledge/frameworks/` — 思考の足場（reasoning_scaffold, rag_design等）
- `knowledge/playbooks/` — 業務別標準手順
- `knowledge/failure_patterns/` — 実際に起きた失敗パターン
- `EVAL_POLICY.md` — 評価基準
- `DECISION_LOG.md` — 重要な意思決定の記録
- `WORKFLOW_SPEC.md` — AI運用設計の全体像

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