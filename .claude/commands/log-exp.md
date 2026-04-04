# log-exp

## Objective
実験完了後に result.md の内容を experiment_ledger.csv に自動追記する。

## When to Use
- 実験が完了して result.md を書いた直後
- 実験台帳を最新化したいとき

## Process

### Step 1: 対象を確認
- カレントの実験ディレクトリを特定（引数があればそれ、なければ直近の experiments/exp*/）
- `result.md` が存在することを確認

### Step 2: result.md から情報を抽出
以下のフィールドを読み取る:
- Experiment ID
- Validation（CV手法）
- Model / Preprocessing
- Mean RMSE（または主要メトリクス）
- Std RMSE
- Overall OOF RMSE（あれば）
- Findings（1行サマリ）
- Next Hypothesis（1行サマリ）

### Step 3: experiment_ledger.csv に追記
`experiments/experiment_ledger.csv` がなければ以下ヘッダーで作成:
```
exp_id,date,validation,preprocessing,model,cv_mean,cv_std,oof_score,findings_1line,next_hypothesis_1line,status
```

新しい行を末尾に追記:
- `status` は `done`
- `date` は今日の日付（YYYY-MM-DD）
- 長い文字列はダブルクォートで囲む

### Step 4: SESSION_NOTES.md を更新
コンペの SESSION_NOTES.md の実験結果セクションに1行追記:
```
- [date] {exp_id}: CV={cv_mean:.2f}±{cv_std:.2f} → {findings_1line}
```

### Step 5: 完了報告
- 追記した行を表示
- ledger のベストスコア上位3件を表示

## Hard Rules
- result.md が存在しない場合は追記しない
- 同じ exp_id が既に ledger にある場合は上書きせず警告を出す
- CSV のカンマ・改行を含む文字列は必ずクォートする
