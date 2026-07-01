---
title: "WandB による実験管理（導入と最低限ログすべきもの）"
type: playbook
domain: ml
tags: [kaggle, wandb, experiment-management, reproducibility, hydra, logging]
created: 2026-06-05
source:
  title: "WandB（Weights & Biases）入門 — 実験迷子を防ぐ"
  author: "Kaggler community（出典記事）"
  isbn: ""
  chapter: ""
---

## Summary
WandB は学習過程（Loss/メトリクス推移）・ハイパーパラメータ・コードバージョン・GPU使用率をクラウドで自動一元管理し、過去実験との重ね合わせ比較を高速にする実験管理ツール。Kaggle上位・研究室・企業で標準。
目的は「実験迷子」の撲滅：`model_v2_hontouni_final.pth` 地獄、再現できない過去設定、手動スプレッドシートの破綻を防ぐ。
中核は `init` / `log` / `finish` の3関数。**Hydra の config を丸ごと `wandb.init(config=...)` に渡す**のが実戦的。
※メトリクス追跡はWandBに一本化し、`result.md` は「実験の意図・採用判断・次仮説」だけを担う（後述）。旧CSV台帳フックは廃止済み。

## Core Principles
- **記録していない実験は無かったのと同じ**。パラメータ・コードVer・曲線を自動で残す（手動メモは続かない）。
- **設定（Config）と結果（Metrics）を分けて記録する**。再現に必要な入力＝Config、評価＝Metrics。
- **実験名は意味のある名前**を付ける（`Exp01_resnet18_lr1e-3` 等）。後から比較できるように。

## Decision Rules
- **WandB を使う場面**：複数実験を回して比較・チューニングするコンペ/研究。曲線の重ね合わせや並べ替えで意思決定する局面。
- **WandB vs ローカル `result.md`（このWSの棲み分け / 2026-06 確定）**：
  - **WandB** = メトリクス追跡の主軸。loss curve・config・実験間比較・クラウド可視化・GPU使用率を自動記録。
  - **`result.md`** = **実験の意図**（なぜこの案・何を確かめたいか）・採用判断・next hypothesis を書き残す叙述的な決定証跡。WandBでは持ちにくい部分だけを担う。
  - → 旧 `experiment_ledger.csv` 自動追記フック（`auto_ledger.py`）は**廃止済み**。CSV台帳は使わない。
  - → メトリクスはWandBで観察、**意図と結論は result.md** に落とす。
- **Hydra と併用するなら**：yaml で管理した config を `wandb.init(config=OmegaConf.to_container(cfg))` で丸ごと渡す（手書き辞書をやめる）。→ [[remote_gpu_runner_kaggle]] の `run.py` 運用と直結。

## Procedure
### セットアップ
```bash
pip install wandb
wandb login        # APIキーを対話入力（https://wandb.ai/settings#apikeys で確認）
```
※ Colab/Kaggle では APIキーを **Secrets 経由**で注入する。キーをコード/コミットに残さない。

### コードへの組み込み（init / log / finish）
```python
import wandb

wandb.init(
    project="atmacup-exp",          # コンペ名など
    name="Exp01_resnet18_lr1e-3",   # 意味のある実験名
    config={                         # ← Hydra cfg を丸ごと渡すと最強
        "learning_rate": 1e-3, "epochs": 10, "batch_size": 32,
        "model_name": "resnet18", "seed": 42,
    },
)
config = wandb.config

for epoch in range(config.epochs):
    # ... train / valid ...
    wandb.log({
        "epoch": epoch,
        "train/loss": train_loss,
        "val/loss": val_loss,
        "val/auc": val_auc,         # コンペ指標
    })

wandb.finish()
```

### Tips
- `config` は dict だけでなく **dataclass** も渡せる（Hydra/OmegaConf の cfg もそのまま）。
- **Slack通知連携**：学習完了/実験終了時に Slack へ通知すると、回している間に別作業へ集中できてQoLが上がる。
- **checkpoint** にはモデルだけでなく optimizer/scheduler の状態も保存すると、途中から再学習できて便利。

## 何をログするか（チェックリスト）
**Config（設定値）**
- 学習率 / エポック数 / バッチサイズ
- モデルアーキ名（例 `tf_efficientnet_b0`）
- シード値
- Optimizer / Scheduler の種類
- CV の Fold 数（どの fold か）

**Log（メトリクス）**
- Train Loss / Valid Loss
- コンペ評価指標（Accuracy / RMSE / AUC / F1 など）
- ※GPUメモリ・温度は WandB が自動記録

## Anti-patterns
- **APIキーをコード/Notebook出力/コミットに残す** → 漏洩。`wandb login` 対話入力か Secrets 経由。
- **WandBに記録したから result.md を書かない** → メトリクスと決定証跡は別物。実験の意図・採用判断・next hypothesis はローカルの result.md に残す。
- **実験名が `test`/`exp` ばかり** → 後で区別できず比較が無意味化。命名規則を決める。
- **seed/foldをConfigに入れ忘れる** → 再現できず、CV比較の前提が崩れる。
- **手書き辞書でconfigを肥大化** → Hydra yaml に寄せて `wandb.init(config=...)` で渡す。

## Example
画像コンペでfold別に実験：
1. Hydra で `configs/exp01.yaml`（lr/model/seed/fold）を定義。
2. `run.py` 冒頭で `wandb.init(project=..., name=f"exp01_fold{cfg.fold}", config=...)`。
3. epoch毎に `wandb.log({"val/auc":..., "val/loss":...})`、`wandb.finish()`。
4. WandBで5fold曲線を重ねてOOFの安定性を確認 → 採用可否と次仮説は `result.md` に記録。

## Eval
- Config に seed / fold / model / optimizer が漏れなく入っている。
- メトリクスが train/val で分けて記録され、コンペ指標が含まれる。
- APIキーがコミット・出力に残っていない。
- WandBの観察結果が `result.md` の意図・採用判断に接続されている（観察止まりでない）。

## 関連
- [[remote_gpu_runner_kaggle]] — Hydra+run.py の thin switch 実行環境（configをそのままwandbへ）
- [[image_baseline_tuning_kaggle]] — ここで回す学習レシピ
- [[experiment-workflow]] — result.md / SESSION_NOTES への記録ステップ
