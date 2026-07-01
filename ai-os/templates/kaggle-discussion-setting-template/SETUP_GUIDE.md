# Discussion Knowledge Base — Setup Guide

This guide walks through setting up the discussion knowledge base for a new Kaggle competition.
All steps are deterministic and can be executed by any model/session.

## Prerequisites

- Kaggle MCP server configured and accessible（接続できない場合は `KAGGLE_MCP_AUTH.md` 参照）
- ワークスペース直下 `C:/workspace/.claude/agents/` に以下が配置済み（インストール済み）:
  - `discussion-fetcher.md` (sonnet) — raw JSON取得
  - `discussion-card-writer.md` (sonnet) — カード生成
  - `discussion-updater.md` (sonnet) — 差分更新
  - `discussion-reviewer.md` (opus) — 品質レビュー
  - `insight-organizer.md` (sonnet) — INSIGHTS構造整備
- ワークスペース直下 `C:/workspace/.claude/commands/` に以下が配置済み:
  - `fetch-discussions.md`, `build-cards.md`, `update-discussions.md`
  - `build-index.md`, `review-discussions.md`, `organize-insights.md`, `kaggle-discussion-setup.md`

## Forum IDの見つけ方

```
# 方法1: MCPでフォーラム一覧を取得
mcp__kaggle__list_forums で competition slug を検索

# 方法2: 任意のdiscussion JSONから取得
mcp__kaggle__get_forum_topic で1件取得 → forum_topic.forum_id
```

## Recommended Setup

`/kaggle-discussion-setup <slug> [forum-id]` を実行すれば下記 1-5 を一括で行う。
手動でやる場合は以下を参照。

## Paths

- **テンプレ元**: `C:/workspace/ai-os/templates/kaggle-discussion-setting-template/`
- **既定の構築先**: `C:/workspace/ai-os/projects/<slug>/kaggle-discussions/`
  - 別の場所に置きたい場合は `/kaggle-discussion-setup --target <dir>` か手動で

## Setup Steps

### 1. Copy template to target directory

PowerShell:
```powershell
$src = "C:/workspace/ai-os/templates/kaggle-discussion-setting-template"
$dst = "C:/workspace/ai-os/projects/<slug>/kaggle-discussions"
New-Item -ItemType Directory -Force (Split-Path $dst)
Copy-Item -Recurse $src $dst
```

Bash:
```bash
SRC=C:/workspace/ai-os/templates/kaggle-discussion-setting-template
DST=C:/workspace/ai-os/projects/<slug>/kaggle-discussions
mkdir -p "$(dirname "$DST")"
cp -r "$SRC" "$DST"
```

### 2. Rename template files

構築先で:
```bash
cd <DST>
mv README_TEMPLATE.md README.md
mv CLASSIFICATION_RULES_TEMPLATE.md CLASSIFICATION_RULES.md
mv INSIGHTS_TEMPLATE.md INSIGHTS.md
rm SETUP_GUIDE.md KAGGLE_MCP_AUTH.md  # テンプレ側に残っているので不要
```

### 3. Fill in competition-specific info in README.md

Replace all `{{placeholder}}` values:
- `{{COMPETITION_SLUG}}` — e.g., `nvidia-nemotron-model-reasoning-challenge`
- `{{FORUM_ID}}` — e.g., `10085877`
- `{{DATE}}` — today's date in YYYY-MM-DD
- `{{TOTAL}}` — (unknown) で初期化、fetch後に更新
- **Card language** — Key Design Decisionsに言語を記載（例: `日本語`）

### 4. Create data directories

```bash
mkdir -p raw/topics raw/threads cards notebooks issues index
```

### 5. Initialize fetch_status.md

Create `index/fetch_status.md` with initial state:

```markdown
# Fetch Status
- **Competition**: {{COMPETITION_SLUG}}
- **Forum ID**: {{FORUM_ID}}
- **Last fetched**: (not yet)
- **Total topics (API count)**: (unknown)
- **Topics fetched**: 0
- **Sort order**: New (newest first)

## Fetch History
| Date | Page | Topics Added | Cumulative |
|------|------|-------------|------------|
```

## Workflow: Initial Build

初回構築は以下の順序で行う:

### Phase 1: データ取得 & カード生成（最初の20件）

```
/fetch-discussions          # 最新20件を取得
/build-cards                # カード生成（topic_typeはTBD）
```

### Phase 2: ルール設計

20件のカードを読み、以下を設計:
1. `CLASSIFICATION_RULES.md` — topic_type分類基準を記入
   - `question`乱用防止ルールを必ず書く
   - primary type選定基準を具体例付きで書く

### Phase 3: 残り全件取得

```
/fetch-discussions          # 次の20件を取得（繰り返し）
/build-cards                # カード生成（ルール適用済み）
/review-discussions         # Opusでレビュー（10件ずつバッチ）
/build-index                # インデックス構築
```

**ワークフロー: fetch → build-cards (sonnet) → review (opus, バッチ) → build-index (sonnet)**

### Phase 4: 横断整理

- レビューで出たissues/昇格候補をもとに `issues/*.md` を作成
- 初回TBDだったカードのtopic_typeをバッチ更新

## Workflow: Ongoing Maintenance

```
/update-discussions          # 新規・更新topicの差分取得
/build-cards                 # 新規分のカード生成
/review-discussions          # レビュー
/build-index                 # インデックス再構築
```

## Known Pitfalls (今回の構築で判明)

| 問題 | 原因 | 対策 |
|------|------|------|
| sticky topicがページ間で重複 | Kaggle APIの仕様 | topic_idで重複排除（fetcher指示書に記載済み） |
| Comments数が過小 | comments配列長を使用 | `total_messages`を使う（card-writer指示書に記載済み） |
| Last Comment が N/A | コメントなしtopic | Posted日付をfallback（CARD_TEMPLATE記載済み） |
| Related Topicの捏造 | Sonnetが推測でidを付与 | スレッド内URLから抽出したもののみ記載（card-writer指示書に記載済み） |
| Opusレビューでraw JSONを「空」と誤判定 | Readツールのトークン上限 | ファイルサイズ確認後に判断（reviewer指示書に記載済み） |
| question分類の乱用 | タイトルが質問形式だと安易にquestionにされる | CLASSIFICATION_RULESに乱用防止ルール記載 |
| タイトル省略 | インデックス生成時に切り詰め | build-index指示書にタイトル全文記載ルール |
| raw JSONが壊れている（パースエラー） | SonnetがWriteツールで大きなJSONを保存する際にトランケーション | fetcher指示書に保存後のJSON検証ステップを組み込み済み。検証失敗時は自動再取得 |
| fetcherが既存ファイルと誤認してスキップ | 旧ディレクトリの同名ファイルをGlobで拾う | fetcher指示書のGlob対象を `kaggle-discussions/raw/threads/` に限定（パス指定を厳密に） |
| `/command-name` が Unknown skill | `.claude/command/`（単数）に置いている | 正しくは **`.claude/commands/`（複数形）**。Claude Codeは `commands/` を参照する |
| コメント更新の見逃し | `Last fetched`が日付のみだと、同時刻帯のコメントを`>`比較で取りこぼす | `Last fetched`をISO 8601 datetime（`YYYY-MM-DDTHH:MM:SSZ`）で保存し、比較は `>=` を使用（updater指示書に記載済み） |
| sortByの選択ミス | APIのsortByオプションの挙動が直感と異なる | 下記「MCP API sortByの挙動」参照。**必ず `New` を使う** |

## MCP API sortByの挙動（検証済み）

| sortBy | 実際のソート順 | 差分更新に使えるか |
|--------|---------------|-------------------|
| `New` | **post_date降順**（投稿日が新しい順） | 新規topic検出に使える。コメント更新検出には全ページスキャン必要 |
| `Active` | **comment_count降順**（コメント数が多い順） | **使えない。** last_comment_date順ではない |
| `Top` | **votes降順** | **使えない。** vote変動でページ間移動が起きる |
| `Hot` | 不明（Hot独自アルゴリズム） | 信頼性不明 |
| `Recent` | 未検証 | — |
| oldest順 | **存在しない** | — |

**結論:** 差分更新は `sortBy="New"` で全ページスキャンし、各topicの `last_comment_post_date` を `Last fetched` と比較する方式が最も確実。
