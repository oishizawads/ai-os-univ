---
name: build-cards
description: 取得済みraw JSONからknowledge cardを生成する
---

# Build Cards

`kaggle-discussions/raw/threads/` にある未処理のthread JSONからknowledge cardを生成する。

## 手順

1. `kaggle-discussions/raw/threads/` のJSONファイル一覧を取得
2. `kaggle-discussions/cards/` の既存カード一覧を取得
3. 未生成のtopic_idリストを特定
4. discussion-card-writerエージェント（sonnet）を起動する:
   - `topic_ids`: 未生成のtopic_idリスト
5. エージェント完了後、生成されたカードの数を報告

## 注意

- 大量の未生成カードがある場合、10-15件ずつバッチで処理する
- カード生成後、品質をざっと確認する（最初の数件を読む）
- CLASSIFICATION_RULES.mdが「NOT YET DESIGNED」の場合、topic_typeはTBDになる
