# Harness Engineering ワークフロー

## フロー概要

```
人間: 要求Issue作成 → status:requirement + agent:claude 付与
   ↓
[Claude] Issueコメントで壁打ち → 要件確定
   ↓ status:design + agent:claude
[Claude] 詳細設計・実装Issue分割
   ↓ 子Issueに status:ready + agent:codex
[Codex] 実装 → PR作成
   ↓ status:review + agent:claude
[Claude] コードレビュー → 修正指示
   ↓ status:review + agent:codex
[Codex] 修正 → PR更新
   ↓ (CI green + レビューOK)
[人間 or 自動] マージ → status:merged
```

## ステップ別の手順

### Step 1: 要求Issue作成（人間）

1. GitHub で Issue を作成（テンプレ: **要求 Feature Request** を選択）
2. 背景・ゴール・受け入れ条件・制約を記入
3. ラベル付与: `status:requirement`, `type:feature`, `priority:xxx`

### Step 2: 要件定義（Claude = PM）

Issueを見て以下を行う:
```
@claude このIssueの要件を詰めてください
```
または Claude Code で:
```
/要件定義 Issue #xxx
```

Claude がやること:
- 不明点を箇条書きでIssueコメントに投稿
- 人間が回答
- 要件が確定したら「要件確定」とコメント＋`status:design`に変更

### Step 3: 詳細設計・タスク分割（Claude = PM）

要件確定後、Claudeが以下を行う:
- 実装方針・影響範囲を設計書としてIssueコメントに投稿
- 実装を子Issueに分割（1 Issue = 1 PR を原則）
- 各子Issueに `status:ready`, `agent:codex` を付与

### Step 4: 実装（Codex = Engineer）

子Issueを対象に Codex を起動:
```bash
# ローカルで手動起動 (P2フェーズ)
/codex:rescue Issue #xxx を実装してください。仕様は Issue の本文を参照。

# GitHub Actions 経由 (P3フェーズ以降)
# status:ready ラベルで自動起動
```

Codex がやること:
- コード実装
- テスト作成
- PR作成（タイトルに `closes #xxx` を含める）
- ラベルを `status:review`, `agent:claude` に更新

### Step 5: レビュー（Claude = PM）

PR に対してレビューを実施:
```
/review PR #xxx
```

Claude がやること:
- コードレビュー（4カテゴリ: 仕様整合 / セキュリティ / 品質 / テスト）
- レビューコメントをPRに投稿
- 問題なければ Approve / 修正が必要なら `agent:codex` に戻す

### Step 6: マージ

- CI green + Claude Approve でマージ
- 親Issueの受け入れ条件をすべて満たしたら親Issueをclose

## ブロッカー依存の管理

Issue A が Issue B をブロックする場合:
1. Issue B に `status:blocked` を付与
2. Issue B の本文に `blocked by #A` を記載
3. Issue A がcloseされたら手動で Issue B を `status:ready` に変更
（P4でこれを自動化する）

## モデル切替ポリシー

| 場面 | モデル |
|------|--------|
| 通常の要件壁打ち | 既定モデル |
| 複雑なアーキ判断 | 上位モデル（手動切替） |
| 実装 | Codex (gpt-5.4) |
| 通常レビュー | 既定モデル |
| 重要案件レビュー | 上位モデル（手動切替） |

## コマンドリファレンス

| コマンド | 用途 |
|---------|------|
| `/codex:rescue Issue #xxx を実装` | Codex に実装委譲 |
| `/review` | PR レビュー |
| `Agent(experiment-planner)` | 要件整理・実験設計 |
| `Agent(planner)` | 実装計画立案 |
| `Agent(code-reviewer)` | コードレビュー |
