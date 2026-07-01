---
name: review-discussions
description: Opusによるdiscussionカードの品質レビュー + INSIGHTS.md記録
---

# Review Discussions

Opusレビューエージェントを起動し、カードの品質・分類・見逃し知見を検出し、INSIGHTS.mdに情報を記録する。

## 使い方

引数なし: 直近生成分（未レビュー分）を対象にフルレビュー
引数あり: 指定した焦点でレビュー

例:
- `/review-discussions` — 未レビュー分のフルレビュー
- `/review-discussions classification` — 分類の正確性チェック
- `/review-discussions missed_insights 684212 685920` — 特定topicの見逃し確認
- `/review-discussions insights` — INSIGHTS.mdへの情報記録のみ

## 手順

1. discussion-reviewerエージェント（**opus**）を起動する
   - `focus`: 引数から判定（デフォルト: `all`）
   - `topic_ids`: 引数から判定（デフォルト: 直近生成分）
2. レビュー結果を確認
3. 修正されたカードがあればインデックス再構築（`/build-index`）
4. issues/昇格候補があれば、ユーザーと相談して作成

## 注意

- Opusエージェントなのでコスト高。全129件を一度にレビューしない
- 10-20件ずつバッチで実行するのが推奨
- 新バッチ取得後のルーティンとして `/build-cards` → `/review-discussions` の順で実行
- レビュー中にdiscussionから得られた情報はINSIGHTS.mdに記録される
