# SESSION_NOTES.md

## Project
Near Infrared Challenge

## Current Goal
CV再現性を保ちながら、baselineを起点に前処理・validation・特徴量の改善余地を見極める。

## Best So Far
- Best experiment: expA003_pls
- Best CV OOF: 12.49 / fold mean: 12.40 / fold std: 1.51
- Validation: KFold(n_splits=5, shuffle=True, seed=42)
- Seed: 42
- Model: PLSRegression(n_components=25)
- Preprocessing: raw
- Public LB: 未提出

## Current Reliable Baseline
- Experiment ID: expA002_kfold_baseline
- Validation: KFold_5 (shuffle=True, seed=42)
- Features: 波数列1555本(raw)
- Model: Ridge(alpha=1.0)
- Why this is trusted: KFold OOF=18.62がpublic LB=21.5に近く追跡基準として適切。std=1.46で安定。

## CV設計の決定記録
- GroupKFold(species)はfold4(species 3,4)が壊滅的(RMSE=73.76)で全体OOF=42.44に。CVとして悲観的すぎ。
- KFold OOF=18.62 ≒ public LB=21.5 → KFoldを追跡基準に採用
- KFoldのバイアス（約3pt楽観）は常に意識する
- 改善判断: KFold OOFが下がれば本物とみなす

## What We Know
- この課題は RMSE 評価の回帰タスク
- 前処理と validation 設計が重要
- 再現できない改善は採用しない
- public LB だけでは判断しない
- **trainとtestで樹種(species_number)が完全に非重複** → 未知樹種への汎化が本質
- fold4のように特定樹種では大きく精度が落ちる構造的な難しさがある

## What Failed
- Idea: PLS + KFold (expA003, n=20)
- Why it failed: KFoldは樹種leakがあるため楽観的すぎ。PLS(n=20) KFold OOF=13.12 → LB=31.83に悪化。PLSはnが大きいほど樹種固有パターンを学習してしまう。
- Whether to retry: KFoldをPLS評価に使うのは禁止。GroupKFoldで評価すること。

## Current Hypotheses
- SNV や SG 系前処理が有効かもしれない(樹種間の差を吸収できる)
- fold4の悪化は特定樹種のスペクトル特性の違いが原因の可能性
- validation 設計によって見かけの改善が起きる可能性がある

## Leakage / Validation Concerns
- suspicious columns or transformations: tree_species / species_number を特徴量に混入させない
- split mismatch risk: KFoldではなくGroupKFold必須(樹種leak防止)
- preprocessing fit/transform mismatch risk: fold外でfitしない

## Open Questions
- fold4が悪い樹種は何か(OOF分析で確認できる)
- SNV等の前処理でfold間ばらつきが改善するか
- Ridge以外(PLS、LightGBM)との比較

## Next Experiment Queue
1. expA002: SNV前処理の差分比較
2. expA003: PLS回帰との比較
3. fold別OOF分析(どの樹種が難しいか)

## Decision Rules
- CV が不安定な案は本命にしない
- std が悪化する改善は慎重に扱う
- public LB のみ良い案は採用しない
- baseline より複雑なのに説明できない案は保留

## Warnings
- leakage に注意
- train / inference の不整合に注意
- 一発屋のスコア改善を信用しない
---
## Session Log 2026-04-01 23:51

**編集ファイル:**
- .claude\settings.json
- ai-os\.claude\skills\slides-maker\SKILL.md
- ai-os\.claude\skills\slides-maker\references\design-system.md
- ai-os\hooks\lib\rotate_daily_report.py
- ai-os\hooks\lib\session_notes_sync.py
- ai-os\hooks\rotate-daily-report-hook.sh
- ai-os\hooks\suggest-claude-md-hook.sh
- ai-os\hooks\sync-session-notes-hook.sh
- competitions\near-infrared-challenge\.steering\2026-04-01-expA001-baseline\design.md
- competitions\near-infrared-challenge\.steering\2026-04-01-expA001-baseline\tasklist.md
- competitions\near-infrared-challenge\SESSION_NOTES.md

**実行コマンド（抜粋）:**
- `ls /c/workspace/`
- `ls /c/workspace/competitions/`
- `ls /c/workspace/competitions/near-infrared-challenge/`
- `ls /c/workspace/competitions/near-infrared-challenge/data/`
- `ls /c/workspace/competitions/near-infrared-challenge/data/raw/`

---
## Current GroupKFold Top 5

- 1. `expA005_deriv_corr_pls` / `expA006_deriv_corr_pls_top100`: SG1 + correlation top-100 + PLS, OOF RMSE = 24.365418
- 2. `expA024_ipls_pls` / `expA017_ipls_pls`: iPLS-style interval selection + PLS, OOF RMSE = 25.234007
- 3. `expA025_water_band_pls` / `expA018_water_band_pls`: water-band-focused interval + PLS, OOF RMSE = 25.736486
- 4. `expA004_snv_pls`: SNV + PLS, OOF RMSE = 27.847695
- 5. `expA026_cars_like_pls`: CARS-like selection + PLS, OOF RMSE = 29.430584

## Current Practical Ranking Notes

- The strongest family right now is PLS with interval-style or stability-oriented wavelength selection.
- iPLS-style and water-band interval models are the most promising follow-ups after the top-100 correlation PLS line.
- Ridge-family models are currently weaker than the top PLS-family runs under `GroupKFold(species)`.
