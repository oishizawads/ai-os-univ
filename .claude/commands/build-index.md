---
name: build-index
description: topic_catalog.md インデックスを再構築する
---

# Build Index

`kaggle-discussions/cards/` の全カードから `kaggle-discussions/index/topic_catalog.md` を再構築する。

## 手順

1. `kaggle-discussions/cards/` の全カードをGlobで列挙
2. 各カードからメタ情報を抽出:
   - Topic ID, Title, Author, Votes, Comments, Posted, Last Comment, Topic Type
3. `index/topic_catalog.md` を以下の構造で生成:

```markdown
# Discussion Catalog
Last updated: {今日の日付}
Total topics indexed: {N}

## All Topics (by Votes, Top 30)
| ID | Title | Votes | Cmts | Author | Type | Posted | Updated |
|----|-------|-------|------|--------|------|--------|---------|
| ... (votes降順) |

## By Type (primary type only)
### {type_name}
| ID | Title | Votes | Updated |
(各topicはprimary type=最初のtypeのセクションにのみ表示。重複しない)

## Recently Updated (7 days)
| ID | Title | Votes | Last Comment |
```

4. 生成した `topic_catalog.md` をWriteで保存

## 重要なルール

### タイトルは省略しない
- タイトルは**全文を記載**する。`…` で省略しない
- テーブルの幅が広くなっても構わない。情報の正確性が最優先

### By Typeは複数タグに重複掲載OK
- 複数タイプを持つtopicは**全該当セクションに掲載**する
- 情報の見逃し防止が最優先。冗長は許容する
- 例: `official, metric_issue` → `official` セクションと `metric_issue` セクションの両方に掲載

### Updated列のN/A禁止
- Last Commentが空/N/Aの場合、Posted日付をfallbackとして使用する
- 「N/A」「—」は使わない

### Comments数の正確性
- `forum_topic.total_messages` を使う（コメント配列の長さではなく）

### votes降順がメインソート
- All Topics, By Type内、Recently Updated — 全てvotes降順
- Topic Typeが「TBD」のカードは「Unclassified」セクションにまとめる
- All Topicsセクションは上位30件まで表示し、残りはBy Typeセクションで参照

