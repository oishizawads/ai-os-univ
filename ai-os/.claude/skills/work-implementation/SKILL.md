---
name: work-implementation
description: 業務案件を要件整理から実装・記録まで進める
---

# Work Implementation

## Phase 0: Read Context
- `CLAUDE.md` を読む
- `PROJECT.md`, `DATA_CONTRACT.md`, `SESSION_NOTES.md` を読む
- `docs/` と `meeting_notes/` の関連ファイルを確認する
- 目的、利用者、KPI、制約を要約する

## Phase 1: Define Scope
- 今回やること / やらないことを明示する
- 成果物を定義する
- 曖昧な点は `assumptions.md` に書く前提で整理する

## Phase 2: Steering
- `.steering/requirements.md`, `design.md`, `tasklist.md` を起点に考える
- 実装の前に要件と設計の整合を確認する

## Phase 3: Implement
- `src/` は本命コード、`ai-src/` は試作コードとして扱う
- 変更理由、影響範囲、リスクを明示する
- 必要に応じて分析コードと業務コードを分ける

## Phase 4: Review
- 要件と実装のズレを確認する
- データ前提、例外処理、設定管理を確認する
- 必要に応じて Codex レビューを前提にまとめる

## Phase 5: Record
- `SESSION_NOTES.md` を更新する
- `meeting_notes/` または `reports/` に要点を残す
- 今回の成果物と未解決事項を整理する

## Output Format
- Objective
- Scope
- Deliverables
- Risks
- Change summary
- Next actions