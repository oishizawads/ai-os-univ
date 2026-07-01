# Harness Runbook

ラベルごとに「誰が・何を・どうやるか」をまとめた実践手順書。

## 使い方

1. 現在のIssueラベルを確認
2. 該当セクションを開く
3. コマンド/プロンプトをコピペして実行

## P4自動遷移コマンド一覧（Issueコメントに書くだけ）

| コメント | 遷移 | 備考 |
|---------|------|------|
| `要件確定` | → status:design | Claudeが自動で設計開始 |
| `設計確定` | → status:ready | Codexへバトン |
| `実装開始` | → status:implementing | 実装中フラグ |
| `レビュー依頼` | → status:review | Claudeが自動でレビュー開始 |
| `マージOK` | → status:merged + close | Issue自動クローズ |
| `ブロック` | → status:blocked | 人間判断待ち |

---

## `status:requirement` — 要件定義中

**担当**: Claude (PM)
**トリガー**: 人間が要求Issueを作成してラベルを付与 → Claudeが自動で壁打ち開始

### P4自動（推奨）

1. Issueに `status:requirement` ラベルを付与
2. GitHub Actions が自動で Claude に要件壁打ちを依頼
3. Claudeの確認事項に回答する
4. 要件が固まったら **「要件確定」** とコメント → 自動で `status:design` へ遷移

### 手動（フォールバック）

```bash
bash transition.sh <issue#> design
```

**完了条件**: 受け入れ条件が全て具体的になっている

---

## `status:design` — 設計中

**担当**: Claude (PM)
**トリガー**: `status:requirement` からの遷移 → Claudeが自動で設計開始

### P4自動（推奨）

1. `status:design` ラベル付与で GitHub Actions が自動起動
2. Claudeが設計書とタスク規模判定をIssueコメントに投稿
3. 設計を確認する（実装方針・PR分割・推奨エージェント）
4. 子Issueを手動で作成（設計コメントからコピペ）
5. 各子Issueに適切なエージェントを割り当て
6. 設計に合意したら **「設計確定」** とコメント → 自動で `status:ready` へ遷移

### タスク規模判定と割り当て

| 規模 | 目安 | 割り当て |
|------|------|---------|
| 軽量 | < 1h / 単一ファイル | Claude 直接 / OpenCode (/opencode-coder) |
| 中規模 | 1-4h / 複数ファイル | Codex CLI |
| 重量 | 4h+ / アーキ変更 | Codex + 人間レビュー |

### 手動（フォールバック）

1. `prompts/02-design.md` のプロンプトをClaude Codeに貼り付けてIssue番号を指定
2. 設計を確認・承認後、子Issueを作成

```bash
bash transition.sh <child-issue#> ready
```

**完了条件**: 子Issueが全て作成され `status:ready` になっている

---

## `status:ready` — 実装待ち

**担当**: Claude直接 / Codex / OpenCode
**トリガー**: 設計完了後に子Issueに付与

### 軽量タスク

Claude 直接実行が既定。量産・並列・トークン実利がある時のみ OpenCode へ委譲:

```bash
python C:/workspace/tools/opencode_coder.py "<タスク説明>"
```

### 中〜重量タスク（Codex）

```
/codex:rescue Issue #<issue#> を実装してください。
仕様は Issue 本文の「実装仕様」セクションを参照。
PR作成まで行ってください。PRタイトルに「closes #<issue#>」を含めること。
```

実装完了後: **「レビュー依頼」** とコメント → 自動で `status:review` へ遷移

### 手動遷移

```bash
bash transition.sh <issue#> review
```

**完了条件**: PRが作成されている

---

## `status:implementing` — 実装中

**担当**: Codex (Engineer)
**状態**: Codex が動作中

### やること

- 基本は待つ
- Codex が詰まっているようなら追加指示を出す
- PR が作成されたら **「レビュー依頼」** とコメント → 自動で `status:review` へ遷移

### 手動遷移

```bash
bash transition.sh <issue#> review
```

---

## `status:review` — レビュー中

**担当**: Claude (PM)
**トリガー**: PR作成後 → Claudeが自動でレビュー開始

### P4自動（推奨）

1. `status:review` ラベル付与で GitHub Actions が自動起動
2. ClaudeがPRを検索し、レビュー結果をIssueコメントに投稿
3. レビュー結果を確認する
4. 問題なし → **「マージOK」** とコメント → Issueが自動クローズ
5. 修正必要 → Codexに差し戻し（ `status:ready` に戻す）

### 手動（フォールバック）

1. `prompts/04-review.md` のプロンプトをClaude Codeに貼り付けてPR番号を指定

```bash
# 差し戻す場合
bash transition.sh <issue#> ready
```

**完了条件**: CI green + Claude Approve

---

## `status:blocked` — ブロック中

**担当**: 人間
**状態**: 依存Issueの完了待ち

### やること

1. Issue本文の `blocked by #xxx` を確認
2. 依存Issueがcloseされたら手動で遷移

```bash
bash transition.sh <issue#> ready
```

---

## トラブルシューティング

### Actions が起動しない

- `github.actor == 'oishizawads'` の制限を確認（自分のアカウントで操作しているか）
- ワークフローファイルが `.github/workflows/` にあるか確認

### Codexが途中で止まった

```
/codex:rescue 続きから: Issue #<issue#> のPR作成まで進めてください
```

### レビューでPRが見つからなかった

PRのタイトルまたは本文に `#<issue#>` を含めるとClaudeが自動検索できる。
見つからない場合は手動でレビューを依頼:

```
PR #<pr#> をレビューしてください。（prompts/04-review.md 参照）
```

### レビューで大量の指摘が出た

優先度を下記で判断:
- CRITICAL / HIGH → Codexで修正してから再レビュー
- MEDIUM / LOW → PRコメントに記録して別Issueに切り出す

### 子Issueが多すぎて管理できない

1Issueが30分〜2時間で実装完了できる粒度が目安。
それ以上なら設計フェーズに戻って再分割する。
