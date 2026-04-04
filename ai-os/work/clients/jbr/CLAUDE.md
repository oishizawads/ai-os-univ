# JBR - CLAUDE.md

## Goal
JBR との案件リポジトリ。
需給バランス予測モデルの構築・手配難リスクスコアリングを通じて、データドリブンな配車最適化を実現する。

## Read First
1. `PROJECT.md` — エグゼクティブサマリー・PoCモデル設計
2. `DATA_CONTRACT.md` — データ提供条件・カラム定義・権限
3. `SESSION_NOTES.md` — ロードマップ・次のステップ
4. `docs/data_dictionary.md` — データ定義詳細
5. 直近の `meeting_notes/`

## Project Context
- **Phase 1（現在）**: 既存データで手配難リスクスコアリング PoC
- **Phase 2**: データ基盤正規化・マスタ一元管理・ETL高速化
- **Phase 3**: リアルタイム配車最適化・業者実績フィードバックループ
- **KPI**: 市区町村×サービス×月次の手配難リスクスコア精度
- **契約**: 月額パートナー契約（最低3ヶ月、以降1ヶ月更新）

## Principles
- 実装前に目的・利用者・KPI・制約を確認する
- 不明点は `docs/assumptions.md` に残す
- 会議後は `/log-meeting` で議事録を作成し `SESSION_NOTES.md` も更新する
- `src/` は本命コード、`ai-src/` は試作コード
- 分析結果は意思決定につながる形で残す

## Directory Rules
- `src/` 本命コード
- `ai-src/` AI試作
- `data/` 受領データ（raw は触らない）
- `docs/` business_context / data_dictionary / metrics / assumptions
- `deliverables/` クライアント提出物
- `meeting_notes/` 議事録
- `reports/` 分析レポート
- `daily_reports/` 日次ログ（hook自動生成）

## Workflow
- `.steering/requirements.md`, `design.md`, `tasklist.md` を起点に進める
- 変更時は理由・影響範囲・懸念点を明示する
- 必要に応じて Codex にレビューを依頼する
