# Kaggle Discussion Knowledge Base

## Competition Info
- **Competition**: {{COMPETITION_SLUG}}
- **Forum ID**: {{FORUM_ID}}
- **Setup Date**: {{DATE}}

## Status
- **Last Fetched**: (not yet)
- **Total Topics**: {{TOTAL}} (fetched: 0)
- **Classification Rules**: Not designed yet

## Workflow Commands

| Command | Description |
|---------|-------------|
| `/fetch-discussions` | Fetch next batch of discussions from Kaggle MCP |
| `/build-cards` | Generate knowledge cards from fetched raw JSON |
| `/update-discussions` | Incremental update (new + updated topics) |
| `/build-index` | Rebuild topic_catalog.md index |
| `/review-discussions` | Opus review: classification, missed insights + INSIGHTS.md記録 |
| `/organize-insights` | INSIGHTS.mdの構造整備（見出し統合・除去候補提示） |

### Full Workflow (初回構築)

初回は `/kaggle-discussion-setup` を実行してから以下を行う（詳細は `kaggle-discussion-setting-template/SETUP_GUIDE.md` 参照）。

```
/fetch-discussions → /build-cards (sonnet) → /review-discussions (opus, 10件ずつ) → /build-index (sonnet)
```

### Update Workflow (日常の差分更新)

```
/update-discussions (sonnet) → /build-index (sonnet) → /review-discussions (opus, 新規分のみ)
```

- `/update-discussions` は全ページスキャンで新規topic + コメント更新topicを検出し、thread再取得・カード生成/再生成まで一括実行する
- インデックスは自動更新されないため、完了後に `/build-index` を実行すること
- INSIGHTS.mdの見通しが悪くなってきたら `/organize-insights` で構造整備する
- issues/昇格候補が出たら、ユーザーと相談して作成

## Required .claude/ Files

このシステムが動作するために `.claude/` 配下に以下のファイルが必要。

### Agents (`.claude/agents/`)

| File | Model | Role |
|------|-------|------|
| `discussion-fetcher.md` | sonnet | MCP経由でraw JSON取得・保存 |
| `discussion-card-writer.md` | sonnet | raw JSON → knowledge card生成 |
| `discussion-updater.md` | sonnet | 差分更新（新規+更新topic検出） |
| `discussion-reviewer.md` | opus | カード品質レビュー・見逃し知見検出・INSIGHTS.md記録 |

### Commands (`.claude/commands/`)

| File | Description |
|------|-------------|
| `fetch-discussions.md` | `/fetch-discussions` の手順書 |
| `build-cards.md` | `/build-cards` の手順書 |
| `update-discussions.md` | `/update-discussions` の手順書 |
| `build-index.md` | `/build-index` の手順書（インデックスフォーマット定義含む） |
| `review-discussions.md` | `/review-discussions` の手順書 |
| `organize-insights.md` | `/organize-insights` の手順書 |
| `kaggle-discussion-setup.md` | テンプレートからの初期構築手順 |

### Blueprint (`kaggle-discussion-setting-template/`)

新コンペで `/kaggle-discussion-setup` を実行すると、このテンプレートからコピーして構築する。

## How to Use (for Claude Code)

### まず読むもの
1. Read `INSIGHTS.md` — discussion知見の集約。設計・実装判断の出発点

### 個別のdiscussionを調べる
2. Read `index/topic_catalog.md` — 全topic一覧（votes順）
3. Read `cards/{topic_id}.md` — 個別topicの詳細
4. Read `raw/threads/{topic_id}.json` — 生データ

### Cross-topic themes
5. Read `issues/*.md` for cross-topic analysis notes

## Directory Structure

```
kaggle-discussions/
  README.md                   # This file
  CARD_TEMPLATE.md            # Template for knowledge cards
  ISSUE_TEMPLATE.md           # Template for issue notes
  INSIGHTS.md                 # Curated insights from discussions
  CLASSIFICATION_RULES.md     # Topic type classification criteria
  raw/
    topics/page_NNN.json      # Raw topic list pages from MCP
    threads/{topic_id}.json   # Raw individual thread JSON from MCP
  cards/{topic_id}.md         # Knowledge cards (1 per topic)
  notebooks/{topic_id}/       # Associated notebooks
  issues/                     # Cross-topic theme notes
  index/
    topic_catalog.md           # Main index (read this first)
    fetch_status.md            # Fetch progress tracking
```

## Key Design Decisions

- **Card language**: {{LANGUAGE}} (技術用語は原文保持)
- **Sort: New (newest first)** — post_date is immutable, so page positions are stable
- **Dedup by topic_id** — handles page shifts when new discussions are added
- **Votes as primary filter** — stable, objective, always available regardless of classification status
- **Three-layer access** — index → cards → raw, progressively deeper
- **By Type with duplication** — 複数タグのtopicは全該当セクションに掲載（見逃し防止優先）
- **INSIGHTS.md** — discussion-reviewer (opus) がレビュー中に知見を記録。知識ベースのフロントエンド
