# log-exp

## Objective
実験完了後に「実験の意図・採用判断・次仮説」を `result.md` に書き残し、`SESSION_NOTES.md` を更新する。
※メトリクス（loss curve・CV score 等）の追跡は WandB に一本化したため、CSV台帳への追記は行わない（旧 `auto_ledger.py` / `experiment_ledger.csv` は廃止済み）。

## When to Use
- 実験が完了したとき
- WandBの観察結果から採用判断・次仮説を確定させたいとき

## Process

### Step 1: 対象を確認
- カレントの実験ディレクトリを特定（引数があればそれ、なければ直近の `experiments/exp*/`）

### Step 2: result.md に意図と結論を書く
`result.md` に最低限これを残す（メトリクスの細部はWandBに任せ、ここは「判断」を書く）:
- **Objective / Intent**: なぜこの案を試したか・何を確かめたかったか
- **Validation**: CV手法（fold設計）
- **Result**: 主要メトリクス要約（WandBのrun名/リンクを併記）
- **Findings**: 1行サマリ
- **Next Hypothesis**: 次に何を試すか
- **採用判断**: 採用 / 不採用と、その理由

### Step 3: WandB との対応づけ
- `result.md` に対応する WandB の run 名（例 `exp01_resnet18_lr1e-3`）かURLを記載し、メトリクスを辿れるようにする。

### Step 4: SESSION_NOTES.md を更新
コンペの `SESSION_NOTES.md` の実験結果セクションに1行追記:
```
- [date] {exp_id}: CV={cv_mean:.2f}±{cv_std:.2f} → {findings_1line}（wandb: {run_name}）
```

### Step 5: 完了報告
- result.md に書いた意図・採用判断・次仮説を要約表示

## Hard Rules
- メトリクスの恒久記録は WandB。`result.md` には「意図と判断」を必ず書く（数字の転記だけで終わらせない）。
- CSV台帳（experiment_ledger.csv）への追記はしない（廃止済み）。
