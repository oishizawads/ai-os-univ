---
title: "Hydra + .py スクリプトによる実験管理とフォルダ構成"
type: playbook
domain: ml
tags: [kaggle, hydra, experiment-management, reproducibility, config, folder-structure, wandb]
created: 2026-06-05
source:
  title: "PythonスクリプトとHydraで実験管理する（Kaggle Template）"
  author: "Kaggler community / テンプレ: kami(unonao/kaggle-template)"
  isbn: ""
  chapter: ""
  url: "https://github.com/unonao/kaggle-template"
---

## Summary
実験フェーズは Notebook をやめ、**.py スクリプト + Hydra** で回す。EDA/データ確認だけ Notebook に残す。
Hydra はパラメータを yaml に集約し、**CLIから上書き**（`python train.py learning_rate=0.005`）できるので、コードを書き換えずに実験を回せる＝再現性が壊れない。
フォルダ構成の核は **「コード=メジャー版（実験フォルダ）/ パラメータ=マイナー版（yamlファイル）」**。これで「コードを上書きして前の結果が再現できない」コンペあるあるを根絶する。
この層が [[remote_gpu_runner_kaggle]]（実行）→ [[experiment_tracking_wandb]]（追跡）→ result.md（意図）の上流＝設定管理を埋める。

## Core Principles
- **EDA は Notebook、実験は .py**。学習を何度も回すフェーズで Notebook は破綻する（後述の地獄）。
- **ハードコーディング撲滅**。lr/model/batch_size は yaml に出し、コード本体に数値を書かない。
- **1つの大きな変更 = 1つの実験フォルダ**。過去の自分を裏切らない再現性を物理的に確保する。

## Decision Rules
- **パラメータだけ変える（マイナー版）** → コードはいじらず `conf/002.yaml` を新規作成。`python -m experiments.exp000_sample.run exp=002` で実行。
- **コード/構造を変える（メジャー版）** → `exp000_sample` フォルダを丸ごとコピーして `exp001_resnet` を作る。モデル構造の刷新・前処理ロジックの根本変更がこれ。古いコードが無傷で残り、一瞬で戻れる。
- **素早いスイープ** → yaml を増やさずCLI上書き（`python train.py learning_rate=0.005 batch_size=64`）。本採用する設定だけ yaml に固定。
- **ローカルGPUが無い** → RunPod等のGPUクラウド、または Colab/Kaggle で .py 実行（[[remote_gpu_runner_kaggle]]）。

## Procedure
```bash
pip install hydra-core
```

### Hydra + WandB の最強コンボ
```python
import hydra, wandb
from omegaconf import DictConfig, OmegaConf

@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    # yamlの設定(cfg)をそのままWandBへ。手書き辞書は不要
    wandb.init(project="kaggle-dojo",
               config=OmegaConf.to_container(cfg, resolve=True))
    print(f"学習率: {cfg.learning_rate}")   # cfg.xxx で呼ぶ
    # ... 学習 ...

if __name__ == "__main__":
    main()
```

### フォルダ構成（kaggle-template ベース）
```
kaggle-project/
├── data/                      # コンペのデータ
├── experiments/               # 実験ごとにフォルダを分ける
│   ├── exp000_sample/         # ← メジャー版（コードの大きな変更単位）
│   │   ├── conf/
│   │   │   ├── 001.yaml       # ← マイナー版（パラメータ設定）
│   │   │   └── 002.yaml
│   │   ├── model.py           # この実験のモデル定義
│   │   └── run.py             # 実行スクリプト
│   └── exp001_resnet/         # ← 構造を変えるときは新フォルダ（丸ごとコピー）
│       ├── conf/001.yaml
│       ├── model.py
│       └── run.py
└── utils/                     # 共通の便利関数
```
実行：`python -m experiments.exp000_sample.run exp=002`（メジャー=フォルダ × マイナー=yaml の組で常に同じ実験を再現）。

## Anti-patterns（= Notebook地獄）
- **ハードコーディング**：`lr = 0.005 # lr = 0.01` のコメントアウト増殖で最新設定が不明になる → yaml に出す。
- **セル実行順スパゲッティ**：上のセルを実行し忘れ古い変数のまま下を実行→間違った結果を提出。.py 化で根絶。
- **ipynbコピペ増殖**：`exp002_resnet_latest.ipynb` 地獄。どれに何の工夫を入れたか追えない → 実験フォルダ＋yaml版管理に。
- **コードを上書きして前実験が再現不能** → メジャー版はフォルダごとコピーして残す。

## Example
ResNetのlrだけ振る → `exp001_resnet/conf/003.yaml` を作り `run exp=003`、cfgをwandbに丸投げ、結果の意図を result.md に。
前処理を根本から変える → `exp001_resnet` を `exp002_newprep` にコピーしてから着手（exp001は無傷で残す）。

## Eval
- 学習ロジックを Notebook に直書きしていない（EDAのみNotebook）。
- パラメータが yaml に出ており、コード本体に数値ハードコードが無い。
- 1つの大きな変更ごとに実験フォルダが分かれ、過去実験が再現できる。
- cfg がそのまま WandB に記録されている（手書き辞書を使っていない）。

## 関連
- [[remote_gpu_runner_kaggle]] — この run.py をローカルGPU無しで回す実行環境
- [[experiment_tracking_wandb]] — cfg を丸投げして追跡（OmegaConf.to_container）
- [[image_baseline_tuning_kaggle]] / [[timm_usage]] — run.py の中身（学習レシピ・モデル）
- [[experiment-workflow]] — 意図・採用判断を result.md に残すステップ
