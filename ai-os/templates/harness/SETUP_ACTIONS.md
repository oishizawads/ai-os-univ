# GitHub Actions セットアップ手順 (P3)

## 前提

- Claude Code サブスクリプション済み
- `gh` CLI インストール済み・認証済み
- 対象リポジトリに `install.sh --with-actions` を実行済み

## Step 1: サブスクトークンの取得

Claude Code CLI でトークンを生成する。

```bash
claude setup-token
```

表示されたトークンをコピーする（`sk-ant-` で始まる文字列）。

> トークンはサブスクリプションに紐づく。API課金は発生しない。

## Step 2: GitHub secrets に登録

```bash
# 対象リポジトリで実行
gh secret set CLAUDE_CODE_OAUTH_TOKEN --repo <owner/repo>
# プロンプトが出たらトークンを貼り付けてEnter
```

確認:
```bash
gh secret list --repo <owner/repo>
# CLAUDE_CODE_OAUTH_TOKEN が表示されればOK
```

## Step 3: ワークフローをコミット・プッシュ

```bash
cd <repo_local_path>
git add .github/workflows/
git commit -m "Add Claude Code Action workflows (P3)"
git push
```

## Step 4: 動作確認

### @claude メンション確認 (claude-mention)

1. GitHub でIssueを開く
2. コメントに `@claude こんにちは` と書いて投稿
3. Actions タブで `claude-mention` が起動するのを確認
4. 数分後にClaudeのコメントが返ってくればOK

### status:requirement 自動壁打ち確認 (claude-requirement)

1. Issue を作成
2. `status:requirement` ラベルを付与
3. Actions タブで `claude-requirement` が起動するのを確認
4. Claudeが要件確認コメントを投稿すればOK

### 自動遷移確認 (claude-state-machine)

1. Issue のコメントに `要件確定` と書く
2. Actions タブで `claude-state-machine` が起動するのを確認
3. ラベルが `status:design` に切り替わればOK

### 自動設計確認 (claude-design)

1. Issue に `status:design` ラベルを付与
2. Actions タブで `claude-design` が起動するのを確認
3. Claudeが設計コメントを投稿すればOK

### 自動レビュー確認 (claude-review)

1. PRを作成（タイトルまたは本文に `#<issue#>` を含める）
2. Issue に `status:review` ラベルを付与
3. Actions タブで `claude-review` が起動するのを確認
4. Claudeがレビューコメントを投稿すればOK

## トラブルシューティング

### Actions が起動しない

- `github.actor == 'oishizawads'` の制限を確認（自分のアカウントか）
- workflow ファイルのトリガー定義を確認

### 認証エラー

```
Error: CLAUDE_CODE_OAUTH_TOKEN is invalid
```

→ `claude setup-token` でトークンを再生成してsecretsを更新する

### タイムアウト

15分でタイムアウトする設定になっている。複雑なタスクは分割する。

### Actions 使用量の確認

```bash
gh api /repos/<owner/repo>/actions/runs --jq '.workflow_runs[] | {name, created_at, run_started_at}'
```

月2000分の無料枠内に収まっているか定期確認する。
