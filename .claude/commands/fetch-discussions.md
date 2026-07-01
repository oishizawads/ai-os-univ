---
name: fetch-discussions
description: Kaggle discussionの次のバッチを取得する
---

# Fetch Discussions

Kaggle MCPからdiscussionの次のバッチ（20件/ページ）を取得する。

## 手順

1. `kaggle-discussions/index/fetch_status.md` を読み、現在の状態を確認する
2. `kaggle-discussions/README.md` からforum_idを読む
3. discussion-fetcherエージェント（sonnet）を起動する:
   - `forum_id`: README.mdから取得した値
   - `page`: fetch_status.mdの次の未取得ページ番号
   - `fetch_threads`: true
4. エージェント完了後、結果を報告する
5. 余裕があれば「もう1ページ取得するか？」とユーザーに確認する

## ページ番号の決め方

- New順（最新から）で取得する
- 総ページ数 = ceil(total_topics / 20)
- 最古から取得したい場合: page = 総ページ数 から開始し、デクリメント
- 最新から取得したい場合: page = 1 から開始し、インクリメント
- fetch_status.mdのFetch Historyから既に取得したページを確認し、次のページを決定

## 初回実行時

fetch_status.mdが初期状態（Last fetched: not yet）の場合:
- まずpage=1で取得して総件数を把握
- ユーザーに最新から取るか最古から取るか確認
