# new-project

## Objective
テンプレートから新しいプロジェクトのディレクトリ構造を一発で生成する。

## When to Use
- 新しいコンペに参加するとき
- 新しいクライアント案件が始まるとき

## Process

### Step 1: プロジェクト情報を確認
ユーザーに以下を確認する（不明な場合のみ）:
1. **種別**: `competition` か `client` か
2. **名前**: ディレクトリ名（例: `near-infrared-2026`, `acme-corp`）
3. **説明**: 一行で何をするプロジェクトか

### Step 2: ディレクトリ構造を生成

#### competition の場合
`C:/workspace/ai-os/competitions/<name>/` に以下を作成:
```
<name>/
├── CLAUDE.md          ← テンプレから生成（competition_project）
├── COMPETITION.md
├── DATASET.md
├── METRIC.md
├── VALIDATION_RULES.md
├── SESSION_NOTES.md
├── README.md
├── src/
├── ai-src/
├── experiments/
├── data/
├── submissions/
├── daily_reports/
├── weekly_reports/
├── monthly_reports/
└── research/
```
テンプレ: `C:/workspace/ai-os/templates/competition_project/`

#### client の場合
`C:/workspace/ai-os/work/clients/<name>/` に以下を作成:
```
<name>/
├── CLAUDE.md          ← テンプレから生成（client_project）
├── PROJECT.md
├── DATA_CONTRACT.md
├── SESSION_NOTES.md
├── src/
├── ai-src/
├── docs/
│   ├── business_context.md
│   ├── data_dictionary.md
│   ├── metrics.md
│   └── assumptions.md
├── deliverables/
├── meeting_notes/
├── daily_reports/
├── weekly_reports/
└── monthly_reports/
```
テンプレ: `C:/workspace/ai-os/templates/client_project/`

### Step 3: テンプレファイルをコピーして中身を生成
- テンプレの内容をそのままコピー
- CLAUDE.md の `## Goal` にプロジェクト説明を入れる
- SESSION_NOTES.md の `## Current Objective` に初期目標を入れる

### Step 4: 完了報告
- 作成したパスを一覧表示
- 「次に埋めるべきファイル」を提示（PROJECT.md / COMPETITION.md など）

## Hard Rules
- 既存ディレクトリが存在する場合は上書きせずエラーを出す
- テンプレの構造を勝手に変えない
- 作成後に必ず `/fetch-project-context` を案内する
