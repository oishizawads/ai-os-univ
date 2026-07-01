# ラベル定義

## status（フロー進行状態）

| ラベル | 色 | 意味 |
|-------|-----|------|
| `status:requirement` | #0075ca | 要件定義中（Claudeと壁打ちフェーズ） |
| `status:design` | #cfd3d7 | 設計中（Claudeが詳細設計を作成中） |
| `status:ready` | #e4e669 | 実装待ち（設計確定、Codex起動可能） |
| `status:implementing` | #d93f0b | 実装中（Codex動作中） |
| `status:review` | #0e8a16 | レビュー中（PRにClaudeがレビュー中） |
| `status:merged` | #6f42c1 | 完了 |
| `status:blocked` | #b60205 | ブロック中（依存Issue待ち） |

## type（作業種別）

| ラベル | 色 | 意味 |
|-------|-----|------|
| `type:feature` | #a2eeef | 新機能・改善 |
| `type:bug` | #d73a4a | バグ修正 |
| `type:refactor` | #e99695 | リファクタリング |
| `type:experiment` | #f9d0c4 | 実験・PoC |
| `type:docs` | #fef2c0 | ドキュメント |

## agent（担当エージェント）

| ラベル | 色 | 意味 |
|-------|-----|------|
| `agent:claude` | #0052cc | Claudeが担当中 |
| `agent:codex` | #006b75 | Codexが担当中 |
| `agent:human` | #e4e669 | 人間の判断・入力待ち |

## priority

| ラベル | 色 | 意味 |
|-------|-----|------|
| `priority:high` | #b60205 | 優先度高 |
| `priority:medium` | #fbca04 | 優先度中 |
| `priority:low` | #0075ca | 優先度低 |
