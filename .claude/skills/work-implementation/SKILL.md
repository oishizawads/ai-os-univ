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
Phase 0 のコンテキスト読了後、**product-analyst** を起動する:
```
以下のプロジェクト情報をもとに、業務要件・KPI・利害関係者・成功条件を整理してください。
[PROJECT.md / SESSION_NOTES.md の内容を貼る]
出力: 今回やること / やらないこと / 曖昧な前提
```
product-analyst の出力をもとに、今回やること / やらないことを明示する。
成果物を定義する。残った曖昧な点は `assumptions.md` に書く。

## Phase 2: Steering
- `.steering/requirements.md`, `design.md`, `tasklist.md` を起点に考える
- 実装の前に要件と設計の整合を確認する

## Phase 3: Implement
- `src/` は本命コード、`ai-src/` は試作コードとして扱う
- 変更理由、影響範囲、リスクを明示する
- 必要に応じて分析コードと業務コードを分ける

## Phase 4: Review
実装完了後、以下を**同時に**起動する。

**code-reviewer** に渡すプロンプト:
```
[変更した src/ のファイル群] をレビューしてください。
観点: 型安全性・ログ設計・例外処理・テスト欠落
```

**backend-reviewer** に渡すプロンプト（API/バッチ/インフラ変更がある場合のみ）:
```
APIエンドポイント・設定管理・依存関係をレビューしてください。
観点: セキュリティ・スケーラビリティ・設定の外部化
```

両エージェントの指摘を統合し、要件と実装のズレ・データ前提・設定管理を最終確認する。

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