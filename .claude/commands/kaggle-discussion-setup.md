---
name: kaggle-discussion-setup
description: テンプレートからdiscussion知識ベースを新規構築する
argument-hint: <competition-slug> [forum-id] [--target <dir>] [--lang 日本語|English]
---

# Kaggle Discussion Setup

`C:/workspace/ai-os/templates/kaggle-discussion-setting-template/` をコピーして、コンペ用の discussion 知識ベースを構築する。

## 既定の配置

- **テンプレ元**: `C:/workspace/ai-os/templates/kaggle-discussion-setting-template/`
- **構築先**: `C:/workspace/ai-os/projects/<slug>/kaggle-discussions/`
  - `--target <dir>` で上書き可（例: `--target C:/workspace/kaggle-discussions`）
- **言語**: 既定 `日本語`（`--lang English` で英語）

## 入力

`$ARGUMENTS` をパースして以下を確定する。曖昧なら最初にユーザーに確認:

- `slug`: 必須。Kaggle competition slug（例: `near-infrared-challenge`）
- `forum_id`: 任意。未指定なら `mcp__kaggle__list_forums` で検索するか、ユーザーに尋ねる
- `target`: 任意。未指定なら `C:/workspace/ai-os/projects/<slug>/kaggle-discussions/`
- `lang`: 任意。未指定なら `日本語`

## 手順

### 1. 事前チェック

- テンプレ元が存在することを確認:
  ```
  ls C:/workspace/ai-os/templates/kaggle-discussion-setting-template/
  ```
- 構築先の親ディレクトリ（`ai-os/projects/<slug>/`）が存在するか確認。なければ作成。
- 構築先が既に存在する場合は中断し、ユーザーに上書き可否を確認。

### 2. テンプレートコピー

PowerShell:
```powershell
Copy-Item -Recurse "C:/workspace/ai-os/templates/kaggle-discussion-setting-template" "<TARGET>"
```

Bash:
```bash
cp -r C:/workspace/ai-os/templates/kaggle-discussion-setting-template "<TARGET>"
```

### 3. ファイルリネーム

構築先で:
- `README_TEMPLATE.md` → `README.md`
- `CLASSIFICATION_RULES_TEMPLATE.md` → `CLASSIFICATION_RULES.md`
- `INSIGHTS_TEMPLATE.md` → `INSIGHTS.md`
- `SETUP_GUIDE.md` は削除（テンプレ側に残るため）
- `KAGGLE_MCP_AUTH.md` も削除（テンプレ側参照）

### 4. README.md のプレースホルダ置換

`<TARGET>/README.md` の以下を Edit で置換:
- `{{COMPETITION_SLUG}}` → `<slug>`
- `{{FORUM_ID}}` → `<forum_id>`（不明なら `(未確定)`）
- `{{DATE}}` → 今日の日付（YYYY-MM-DD）
- `{{TOTAL}}` → `(unknown)`
- `{{LANGUAGE}}` → `<lang>`

### 5. データディレクトリ作成

```
<TARGET>/raw/topics
<TARGET>/raw/threads
<TARGET>/cards
<TARGET>/notebooks
<TARGET>/issues
<TARGET>/index
```

PowerShell: `New-Item -ItemType Directory -Force <path>` を各パスに
Bash: `mkdir -p <TARGET>/{raw/topics,raw/threads,cards,notebooks,issues,index}`

### 6. fetch_status.md 初期化

Write で `<TARGET>/index/fetch_status.md` を作成:

```markdown
# Fetch Status
- **Competition**: <slug>
- **Forum ID**: <forum_id or "(未確定)">
- **Last fetched**: (not yet)
- **Total topics (API count)**: (unknown)
- **Topics fetched**: 0
- **Sort order**: New (newest first)

## Fetch History
| Date | Page | Topics Added | Cumulative |
|------|------|-------------|------------|
```

### 7. 完了報告

以下をユーザーに報告:
- 構築先パス
- forum_id が未確定なら「`mcp__kaggle__list_forums` で確認するか、Kaggle discussion URL から取得してください」と案内
- Kaggle MCP が未設定の場合は `C:/workspace/ai-os/templates/kaggle-discussion-setting-template/KAGGLE_MCP_AUTH.md` を参照するよう案内
- 「次に `/fetch-discussions` で最初のバッチを取得してください」と案内

## 注意

- 構築先と作業ディレクトリは一致しないことが多い。**全てのパスは絶対パス**で扱う
- 構築先 README.md 上の `Required .claude/ Files` セクションはワークスペース直下の `.claude/` に既に配置済みのため、新規プロジェクトでは追加作業不要
