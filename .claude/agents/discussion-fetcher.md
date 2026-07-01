---
name: discussion-fetcher
description: Kaggle MCPからdiscussion raw JSONを取得し保存するエージェント
model: sonnet
---

# Discussion Fetcher Agent

Kaggle MCP経由でdiscussion一覧と個別threadのJSONを取得し、`kaggle-discussions/raw/` に保存する。

## 入力パラメータ（呼び出し元から指示される）

- `forum_id`: コンペのフォーラムID
- `page`: 取得するページ番号（1-based、New順）
- `fetch_threads`: 個別threadも取得するか (default: true)

## 手順

### 1. Topic一覧の取得

`mcp__kaggle__list_forum_topics` を呼び出す:
```
request: {
  forumId: {forum_id},
  sortBy: "New",
  page: {page}
}
```

結果を `kaggle-discussions/raw/topics/page_{page:03d}.json` に **Writeツールで** 保存する。
保存後、Bashで以下を実行してJSONの整合性を検証する:
```bash
python3 -c "import json; json.load(open('kaggle-discussions/raw/topics/page_{page:03d}.json'))"
```
検証に失敗した場合、再度MCPから取得して保存し直す。2回失敗したら報告してスキップ。

### 2. 総件数の記録

レスポンスの `count` フィールドから総topic数を読み取る。

### 3. 取得済みtopic_idの確認

`kaggle-discussions/raw/threads/` 内の既存ファイル名からtopic_idリストを取得する（Globで `*.json` を検索）。

### 4. 個別Thread取得（fetch_threads=trueの場合）

一覧の各topicについて:
- topic_idが既にraw/threads/に存在するならスキップ
- 存在しないなら `mcp__kaggle__get_forum_topic` を呼び出す:
  ```
  request: {
    forumTopicId: {topic_id},
    includeComments: true
  }
  ```
- 結果を `kaggle-discussions/raw/threads/{topic_id}.json` にWriteツールで保存
- 保存後、Bashで以下を実行してJSON検証:
  ```bash
  python3 -c "import json; json.load(open('kaggle-discussions/raw/threads/{topic_id}.json'))"
  ```
- 検証失敗なら再取得・再保存。2回失敗したら報告してスキップ

**重要**: 1件ずつ順番に取得すること。並列呼び出しはしない。

### 5. fetch_status.md の更新

`kaggle-discussions/index/fetch_status.md` を読み、Fetch Historyテーブルに行を追加:

```
| {今日の日付} | {page} | {新規取得件数} | {累計取得件数} |
```

ヘッダー部分も更新:
- `Last fetched`: 今日の日付
- `Total topics (API count)`: countフィールドの値
- `Topics fetched`: 累計取得件数
- `Fetched topic IDs`: 全取得済みIDのカンマ区切り（長くなりすぎる場合は件数のみ）

### 6. 完了報告

以下を報告する:
- 取得ページ番号
- 新規取得topic数
- スキップtopic数（既存）
- 総topic数（API count）
- 残りページ数の概算

## 注意事項

- sticky topicは複数ページに重複出現する場合がある → topic_id重複排除で対処
- JSONの保存はWriteツールを使う（Bashのecho/catは使わない）
- エラー発生時はそのtopicをスキップし、エラー内容を報告に含める
