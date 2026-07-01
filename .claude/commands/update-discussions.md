---
name: update-discussions
description: discussion知識ベースの差分更新
---

# Update Discussions

最後のfetch以降に追加・更新されたdiscussionを検出し、知識ベースを更新する。

## 手順

1. `kaggle-discussions/index/fetch_status.md` のLast fetched日付を確認
2. discussion-updaterエージェント（sonnet）を起動する
3. エージェント完了後:
   - 新規・更新件数を報告
   - 重要な新規topic（高votes、HOST投稿など）をハイライト
4. 必要に応じて `/build-index` でインデックスを再構築
