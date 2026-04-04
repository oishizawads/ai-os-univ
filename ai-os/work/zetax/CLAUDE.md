# ZetaX - CLAUDE.md

## Goal
このディレクトリは ZetaX の会社側ナレッジOSである。
目的は、案件、提案、PoC、再利用資産、社内ルールを一貫した運用で管理すること。

## Read First
1. `COMPANY.md`
2. `STRATEGY.md`
3. `SESSION_NOTES.md`
4. 必要に応じて `operations/`, `internal_docs/`, `clients/`

## Principles
- 案件知識と会社知識を分ける
- 一時的な会話より、再利用できる知識を優先して残す
- 提案・PoC・案件進行・社内標準を混ぜない
- 再利用可能なものは `reusable_assets/` に昇格させる
- 重要な意思決定は `SESSION_NOTES.md` と関連文書に残す
- 会社としての強み、勝ち筋、重点テーマを言語化して維持する

## Directory Rules
- `clients/`: 案件別の会社側メモやリンク
- `proposals/`: 提案書、提案ネタ、案件化前メモ
- `poc/`: PoC 資産
- `reusable_assets/`: 再利用テンプレ、プロンプト、コード断片
- `internal_docs/`: 社内向けナレッジ
- `operations/`: 契約、進行、運用ルール
- `meeting_notes/`: 会社側会議メモ

## Workflow
- 新しい提案や案件が出たら、まず目的・対象顧客・提供価値を整理する
- PoC は案件化可能性と再利用性の両方を見る
- 案件で得た知見は reusable_assets か internal_docs に昇格できるか検討する
- セッション終了前に `SESSION_NOTES.md` を更新する

## Review Focus
- 会社としての勝ち筋に合っているか
- 案件化 / 再利用 / 内製資産化のどれに当たるか
- 実務上の価値があるか
- 継続運用しやすい形に整理されているか