---
title: "画像コンペのベースライン構築・I/O高速化・チューニング"
type: playbook
domain: ml
tags: [kaggle, image, baseline, cnn, vit, timm, augmentation, optimization, cv]
created: 2026-06-05
source:
  title: "画像コンペでのベースラインモデルの育て方（tattaka）"
  author: "tattaka（kami 氏経由で共有）"
  isbn: ""
  chapter: ""
  url: "https://speakerdeck.com/tattaka/hua-xiang-konhetenohesurainmoterunoyu-tefang"
---

## Summary
画像コンペ序盤で「育てる前提の良いベースライン」を作る型。中核は3つ：(1) 信頼できる評価軸（CV）を先に固める、(2) 実験サイクルを速くする＝I/Oボトルネックを潰す、(3) 標準スタックで素直に組んでからチューニングする。
ここでの「良いベースライン」＝**自分の実装を把握している / データをリークしていない / CVとLBのどちらを信じるか見極めて適切に評価できている**。これは本ワークスペースの「CV再現性最優先・public LBだけで採用しない」と一致。
迷ったら **ResNet系 + timm + AMP + EMA + warmup + AdamW + flip/rot90** から始める。

## Core Principles
- **良いベースライン = 評価が信頼できるベースライン**。スコアの高さより「CVが信じられるか」が先。実装内容を把握し、リークが無く、CV/LBの信頼度を判断できていること。
- **実験サイクルの速さが正義**。1実験が遅いと試行錯誤が回らない。**まずボトルネックを特定**してから速くする（推測で最適化しない）。
- **素直なスタックで組んでから動かす**。奇をてらわず timm の定番モデルで土台を作り、そこから1つずつ効果を測る。

## Decision Rules
- **CV vs LB**：両者が乖離したら、どちらを信頼するか先に判断する。基本はCV、ただしCV設計の妥当性（fold分割・リーク）を疑う。public LBだけで案を採用しない。
- **ベースモデル選定**：初手は **ResNet系**（学習しやすい・速い）。ViT系（Swin V1/V2, MaxViT, EfficientViT）は学習が重いので土台が固まってから。CNN候補：ResNet / ResNeSt / ConvNeXt V1/V2 / EfficientNet。実装は **timm**（使い方は [[timm_usage]]。`pretrained` はコンペルール確認、特徴量は `num_classes=0`）。
- **I/O最適化の優先順位**：スライドは特に **(1) データロード&前処理** を最初に確認せよと強調。`htop` 等でCPUを見てボトルネック層を特定 → 下のProcedure順に対処。
- **Optimizer**：基本 `AdamW`。うまくいかなければ `SGD`、`muon` も候補。
- **batch_size**：小＝勾配にノイズが乗り局所解回避／大＝方向が正確でGPU並列をフル活用し速い。学習曲線とスコアで決める（どちらが良いかは問題依存）。
- **epoch**：early stopping が発火しない範囲でチューニング。**last = best とは限らない**ので best を別途保持。

## Procedure
### 1. 評価軸を固める
リークの無いCVを設計 → CV/LBの信頼度を判断 → 以後この物差しで全実験を測る。

### 2. I/Oボトルネックを潰す（実験サイクル高速化）
**(a) データロード&前処理（I/O・CPUバウンド）**
- DataLoader の `num_workers` を適切に増やす（マルチプロセス読み込み）。
- `pin_memory=True`（ページロックメモリ）。
- `jpg`/`png` を `numpy` で保存。精度劣化が無ければ `uint8`/`float16` で保存。
- 可能ならローカルに事前保存してから学習（※実体験で数倍高速化）。

**(b) CPU→GPU転送（PCIeバウンド）**
- GPUメモリが許す限り batch_size を大きく（小バッチ頻繁転送はオーバーヘッド大）。
- `tensor.to(device, non_blocking=True)` で転送と計算をオーバーラップ。

**(c) GPU内部処理**
- *計算律速*（GEMM等が重い：大パラメータ・深い層）／*メモリ帯域律速*（LayerNorm・Dropout・活性化など element-wise が多いとVRAM↔キャッシュが追いつかない）。
- 対策：**AMP（FP16/BF16）** で計算速度とメモリ帯域を同時最適化／**FlashAttention** 等のI/O最適化実装／評価・推論時は必ず `torch.no_grad()`。

### 3. モデル&ヘッドを組む
- timm でベースモデルをロード。
- `drop_path_rate`：層をランダムにスキップ（stochastic depth）。「少し違う浅いネットのアンサンブル」効果で汎化が大きく改善する強力な過学習防止。
- head 設計：層数 / `Dropout`・`BatchNorm` の有無 / Pooling の種類。

### 4. ハイパラをチューニング（学習曲線を見ながら）
下のチートシート参照。

## チートシート（ハイパラ既定値）
| 項目 | 既定/レンジ | メモ |
|------|-------------|------|
| Optimizer | `AdamW` | ダメなら SGD / muon |
| LR (AdamW) | `1e-3`〜`1e-5` | 緩やかに下降→大きく / 振動→小さく |
| LR（層別） | 事前学習部=小, head=大 | head に近づくほど大きく |
| warmup | 基本入れる | 最初に重みを壊しすぎない |
| weight_decay | `1e-2`〜`1e-5` | |
| epsilon | fp32=`1e-8`, fp16=`1e-6` | **fp16で1e-8は0に丸められる** |
| EMA | **ほぼ必須**（初手で） | GM見解「絶対入れる」。`timm.utils.ModelEmaV3`。decayはepoch数に合わせ調整。loss curveが安定 |
| Label Smoothing | `[0.9, 0.05, 0.05]` 等 | ノイズラベル耐性 |
| 正規化 | データセット固有統計を推奨 | ImageNet統計より自データセットの mean/std が効くことが多い。**fold毎に算出**。画像単位/系列単位が効くことも |
| 解像度 | リソースと相談 | batch_size・学習時間とのトレードオフ |

### Augmentation
- **本質の理解**：augは**データ数を増やすのではなく、epochを通して多様なデータを見せる**手法。よってaugを強めると画像がepochごとに変わり、収束に**必要なepoch数が増え、train_lossの低下が緩やかになる**（少epochで評価すると過小評価しがち）。
- **基本**：`flip`, `rot90`（処理後画像は目視確認する）。
- **常用**：`ShiftScaleRotate`（shift/scale/rotate同時）, `RandomBrightnessContrast`, `CoarseDropout`（黒い矩形マスクで一部を隠す）, `Padding`, `RandomGridShuffle`（質感を学習させたいタスクで効くことがある）。
- **Mixup / Cutmix**：2枚を合成。Mixup=半透明重ね、Cutmix=切り抜き貼り付け。target を混ぜるか loss を混ぜるかを決める。

## 画像コンペ実践レシピ（GM / charm 知見）
実戦から「これだけでいい、他はあまり試さない」と絞られた既定。迷ったらこの構成。

**基本**
- **学習ループは自分で書かない**（pytorch-lightning 等）。
- scheduler：`get_cosine_schedule_with_warmup`（transformers）だけでよい。
- optimizer：**AdamW**。
- augmentation：**albumentations**。
- lr：EfficientNet/ResNet は大きめ（`1e-3`）、ConvNeXt/ViT系は小さめ（`1e-4`）。
- **batch_size を変えても lr はあまり変えない**（そもそも batch_size を変えること自体が少ない。Swin等は大きく8程度しか載らないことも）。

**backbone（timm、pooling/head は自前実装）**
- よく使う pooling：**GeM** / `AdaptiveAvgPool2d`。
- **初手は ConvNeXt-base** が多い（lrが大きいと収束しないことがあるので注意）。基本 ConvNeXt を選び、ダメなら他へ。
- EfficientNet は `_ns`（Noisy Student）付き。SwinTransformer系も強い。
- maxvit：AMPでlossが吹っ飛びやすい→lr小さめ。
- eva：timm READMEでは実は強いがあまり使われない（lr小さめ）。Stable Diffusion系コンペは上位軒並みこれだった。
- ※ここで挙がった以外のbackboneは多くの場合弱い。

**auxiliary loss（低コストで効く定番）**
- メタデータを**予測するhead**を追加し、本タスクと**同時に予測**する（入力に使うのではない）。実装コストが低く「実質無料」でよく効く場面が多い。

**EMA**
- もはや「絶対入れる」レベル。強制的に入れ、その状態で精度が出るようチューニングする。decayは epoch 数に合わせて調整（`timm.utils.ModelEmaV3`）。
- **decayの目安**：αが大きすぎると検証精度の向上が遅い。100epoch学習なら `0.9999`→`0.999` 程度が良さそう。`ModelEmaV2`→`ModelEmaV3` は減衰率を調整できる warmup が追加されている。

## Anti-patterns
- **ボトルネックを特定せず最適化に着手** → 効かない箇所を弄って時間を溶かす。先に `htop`/プロファイルで律速を見る。
- **public LB だけで採用判断** → shake down。CVの信頼度を先に評価する。
- **fp16 で epsilon=1e-8** → 0に丸められ AdamW が壊れる。fp16/bf16 では `1e-6`。
- **last epoch を best と思い込む** → best を別途保存・選択する。
- **augmentation を目視確認せず投入** → ラベルと整合しない変換（過度な回転・反転）で学習を壊す。画像コンペは特に。
- **評価/推論で `torch.no_grad()` を忘れる** → 不要な計算グラフでVRAMと速度を浪費。

## Example
ローカルGPU無しの画像分類コンペ初手：
1. リーク無しの StratifiedKFold でCVを固定。
2. 画像を `uint8` numpy に事前変換し、`num_workers` 明示・`pin_memory=True`。
3. timm の ResNet を `drop_path_rate` 付きでロード、head は GAP→Dropout→Linear。
4. AdamW(lr 1e-3, wd 1e-4) + warmup + cosine、AMP(bf16)、EMA。
5. aug は flip/rot90 + ShiftScaleRotate + RandomBrightnessContrast。
6. CVで効果を測りながら1つずつ追加。実行は [[remote_gpu_runner_kaggle]] の thin switch で回す。

## Eval
- ベースラインのCVがリーク無しで再現でき、CV/LBの信頼関係を説明できる。
- 実験1サイクルの律速を特定済み（I/O / 転送 / GPU内部のどれか言える）。
- チューニングが学習曲線の観察に基づいている（当てずっぽうでない）。
- fp16時の epsilon、last≠best、aug目視確認の3点を踏み外していない。

## 関連
- [[remote_gpu_runner_kaggle]] — ローカルGPU無しでこの学習を回す実行環境の型
- [[experiment_design]] / [[evaluation_design]] — CV設計・評価の土台
- [[feature_engineering]] — 特徴量側の足場
