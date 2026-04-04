# sync-from-notion

## Objective
Notion ページの内容を読み取り、workspace の適切なファイルに整形して書き込む。

## When to Use
- 新規案件の情報が Notion にまとまっているとき
- Notion の議事録を meeting_notes/ に取り込みたいとき
- プロジェクト情報を PROJECT.md / SESSION_NOTES.md に反映したいとき

## Process

### Step 1: Notion ページを取得
MCP の notion ツールで指定された URL / ページ ID のページ内容を取得する。
子ページ・データベースがある場合は必要に応じて取得する。

### Step 2: コンテンツを分類
取得した内容を以下のカテゴリに分類する:
| 内容の種類 | 書き込み先 |
|-----------|-----------|
| プロジェクト概要・目的・KPI・成果物 | `PROJECT.md` |
| データ定義・前提・制約 | `DATA_CONTRACT.md` |
| ビジネス背景・課題・利害関係者 | `docs/business_context.md` |
| メトリクス・評価基準 | `docs/metrics.md` |
| 不明点・仮定 | `docs/assumptions.md` |
| 議事録・会議メモ | `meeting_notes/YYYY-MM-DD_<topic>.md` |
| 現状のタスク・進捗 | `SESSION_NOTES.md` |
| コンペ情報（ルール・データ・評価）| `COMPETITION.md` / `DATASET.md` / `METRIC.md` |

### Step 3: 対象プロジェクトを確認
- 書き込み先プロジェクトをユーザーに確認（曖昧な場合のみ）
- 例: `work/clients/ケン・リース/` か `work/clients/jbr/` か

### Step 4: ファイルに書き込む
- 既存ファイルがある場合は「上書き」か「追記」かを確認する
- Notion の元の構造をできるだけ保持する
- 空欄・未記載は `-` で残す（補完しない）

### Step 5: 完了報告
- 書き込んだファイルの一覧を表示
- 「Notion 側にあるが workspace に入れられなかった情報」があれば明示する
- `SESSION_NOTES.md` への追記を提案する

## Hard Rules
- Notion の情報を勝手に解釈・補完しない
- 機密情報（個人情報・契約金額等）が含まれる場合は書き込み前に確認する
- 既存ファイルへの上書きは必ず確認を取ってから行う
