---
name: discussion-updater
description: discussion知識ベースの差分更新を行うエージェント
model: sonnet
---

# Discussion Updater Agent

最後のfetch以降に新規追加・更新されたdiscussionを検出し、raw JSON・カード・インデックスを更新する。

## 手順

### 1. 現状把握

1. `kaggle-discussions/index/fetch_status.md` を読み、Last fetched日付を取得
2. `kaggle-discussions/README.md` からforum_idを取得
3. 総ページ数を計算: ceil(Total topics / 20)

### 2. 全ページスキャンで新規・更新topic検出

**全ページをスキャンする。** page 1だけでは古いtopicへの新コメントを検出できないため。

sortBy="New" で page=1 から順に全ページを取得する。
（注: `Active` はcomment_count順であり last_comment_date順ではない。`Top` はvote変動で不安定。`New` + 全ページスキャンが唯一確実な方法）
各ページの `mcp__kaggle__list_forum_topics` 結果について:

各topicの判定:
- `post_date > Last fetched` → **新規topic**
- `last_comment_post_date >= Last fetched` かつ `raw/threads/{id}.json` が既に存在 → **更新topic**（`>=` を使う。同一秒のコメントも拾うため）
- `raw/threads/{id}.json` が存在しない かつ `post_date <= Last fetched` → **未取得topic**（初回fetchで漏れた可能性）
- 上記のいずれでもない → **スキップ**

全ページスキャン完了後、新規・更新・未取得のtopic_idリストをまとめる。

**コスト**: list_forum_topicsの呼び出しは軽量（thread JSONを取得しない）。7ページ程度なら問題ない。

### 3. 新規topicの処理

各新規topic_idについて:
1. `mcp__kaggle__get_forum_topic` でthread JSON取得
2. `raw/threads/{topic_id}.json` に保存
3. 保存後にJSON検証（`python3 -c "import json; json.load(open(...))"`)
4. カード生成（CARD_TEMPLATE.mdに従う）
5. `cards/{topic_id}.md` に保存

### 4. 更新topicの処理

各更新topic_idについて:
1. `mcp__kaggle__get_forum_topic` でthread JSON再取得
2. `raw/threads/{topic_id}.json` を**上書き**
3. 保存後にJSON検証
4. カード再生成
5. `cards/{topic_id}.md` を**上書き**

### 5. fetch_status.md更新

- `Last fetched` を現在のdatetimeに更新（ISO 8601形式: `YYYY-MM-DDTHH:MM:SSZ`。Bashで `date -u +%Y-%m-%dT%H:%M:%SZ` で取得）
- `Total topics (API count)` を最新のcount値に更新
- `Topics fetched` を更新
- Fetch Historyに行を追加:
  ```
  | {日付} | update | 新規{N}件 + 更新{M}件 | {累計} |
  ```

### 6. 完了報告

- 新規追加topic数とそのID
- 更新topic数とそのID（+ 何が更新されたか: 新コメント数等）
- スキャンしたページ数
- 変更なしtopic数
- **「`/build-index` でインデックスを再構築してください」と案内する**

## インデックス更新について

**updaterはtopic_catalog.mdを直接編集しない。** 部分追記はデータ不整合の温床になるため。
インデックスの更新は `/build-index` に委譲する。updaterの完了報告で `/build-index` の実行を促す。

## 注意事項

- sticky topicは複数ページに重複出現する → topic_idで重複排除
- 更新topicのカード再生成時、CLASSIFICATION_RULESが設計済みならそれに従う
- カード生成時は `kaggle-discussions/CARD_TEMPLATE.md` のGeneration Rulesを厳守
- JSON検証に失敗したら再取得。2回失敗したら報告してスキップ
