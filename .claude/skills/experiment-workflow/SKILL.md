---
name: experiment-workflow
description: 競技・研究系の実験を、設計から検証と記録まで一貫して進める。
---

# Experiment Workflow

## Mission
再現可能な実験を、文脈確認、方針選定、実装、検証、記録の順で進める。

## Read Context
最初に読む:
- `CLAUDE.md`
- `COMPETITION.md`
- `DATASET.md`
- `METRIC.md`
- `SESSION_NOTES.md`
- `VALIDATION_RULES.md`
- `.steering/`

必要なら過去の `experiments/*/result.md` を読む。

## Workflow
1. Goal、制約、成功条件、既知リスクを短くまとめる。
2. 方針を2案まで出す。各案は `what / why / risk / validation cost` を書く。
3. 採用案を選び、`requirements.md` `design.md` `tasklist.md` に落とす。
4. 実装は train と inference の整合を崩さず最小変更で進める。
5. 実験前に validation で何を成功とみなすか明文化する。
6. 実験後は `result.md` と `SESSION_NOTES.md` に必ず記録する。学習中のライブ追跡は WandB を併用してよい（観察＝WandB / 決定証跡＝result.md）→ [[experiment_tracking_wandb]]。

## Optional Parallel Help
必要なときだけ並列依頼する:
- `researcher`: 関連手法、失敗例、実装上の注意点の調査
- `data-analyst`: train/test差分、リーク疑い、EDA要点の整理

## Remote GPU
- ローカルGPUが無い場合、Colab/Kaggle の無料GPUを実行環境として使う。ロジックは `src/` + `run.py`（Hydra等）に置き、Notebook はランチャーに留める → [[remote_gpu_runner_kaggle]]。

## Domain Playbooks
- 画像コンペのベースライン構築・I/O高速化・チューニング既定値（ResNet+timm/AMP/EMA/warmup/aug）→ [[image_baseline_tuning_kaggle]]。

## Guardrails
- 目的なしに特徴量やモデルを増やさない。
- validation を曖昧にしたまま実装しない。
- leakage suspicion point を必ず列挙する。
- 変更理由と次仮説を残す。
- `result.md` には最低限 `objective / validation / fold scores / findings / next hypothesis` を残す。

## Output
- Goal
- Candidate strategies
- Selected strategy
- Files to change
- Validation plan
- Risks
- Record plan
