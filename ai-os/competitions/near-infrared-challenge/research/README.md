# Research Knowledge Base

このディレクトリは、実験コードとは別に外部知見を蓄積するための場所です。

## Purpose

- 論文知見を再利用しやすくする
- 過去コンペや類題の勝ち筋を残す
- 次の実験候補を知見ベースで決めやすくする
- `SESSION_NOTES.md` の短期メモと分離して、長期で残る資産にする

## Structure

- `index.md`: 全体インデックス
- `papers/`: 論文メモ
- `competitions/`: 過去コンペや近い課題のメモ
- `methods/`: 今後試すべき手法候補の整理
- `templates/`: 追記用テンプレート

## Writing Rules

- 1ファイル1トピックを基本にする
- タイトルで中身が分かる名前にする
- 事実と解釈を分ける
- 使えそうな実験案を最後に明記する
- URL と参照日を残す

## Update Workflow

1. 論文や類題を見つけたら、対応ディレクトリに新規メモを作る
2. `index.md` にリンクを追加する
3. 実験に直結する知見は `methods/` に反映する
4. 必要なら `SESSION_NOTES.md` に短く要約を残す
