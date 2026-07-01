---
title: "timm の基本的な使い方（画像モデルを1行で）"
type: reference
domain: ml
tags: [kaggle, image, timm, pytorch, pretrained, feature-extraction]
created: 2026-06-05
source:
  title: "timm 入門 — 最新画像モデルを1行で呼ぶ"
  author: "Kaggler community（出典記事 / 開発: Ross Wightman）"
  isbn: ""
  chapter: ""
---

## Summary
timm は PyTorch で最新の画像モデル（CNN/ViT等、1,000種類以上）を1行で呼べるライブラリ。NLPにおける Hugging Face `transformers` の画像版。画像コンペ上位は事実上全員使う。
`timm.create_model(name, pretrained, num_classes)` が基本。`num_classes` を指定すると **Head（最終分類層）を自動で付け替え**、`num_classes=0` で **特徴量抽出器**になる。
ベースラインは ResNet系から（[[image_baseline_tuning_kaggle]]）。

## Core Principles
- **モデルをゼロから実装しない**。timmで「世界中の天才が考えた構造」＋「ImageNet等の学習済み重み」を一瞬で組み込む（バグ温床を避ける）。
- **Head付け替えはtimm任せ**。`num_classes` を渡すだけで出力次元が合う。
- **特徴量が欲しければ `num_classes=0`**。embedding/metric learning/別処理に接続する定番。

## Decision Rules
- **ベースモデル選定**：初手は ResNet系（王道・学習しやすい）。コスパ重視なら EfficientNet系。最新CNNなら ConvNeXt系、Transformerなら ViT/DeiT 系。→ 詳細は [[image_baseline_tuning_kaggle]]。
  - 現場の好み：CNNなら `resnet18d`（dバリアント）、EfficientNetは `*_ns`（Noisy Student）付きが強いとされる。torchvisionのResNetでなく timm を使うのが画像コンペの基本。
- **`pretrained` の判断**：通常は `pretrained=True`（学習済み重みで強くなる）。**ただしコンペによっては事前学習重みの使用が禁止**されている。必ずルールを確認し、禁止なら `pretrained=False`。
- **`num_classes` の指定**：分類タスクのクラス数。特徴量だけ欲しいときは `0`。

## Procedure
```bash
pip install timm
```

### モデル検索
```python
import timm
# 名前に "resnet" を含み、学習済み重みがあるモデル一覧
models = timm.list_models('*resnet*', pretrained=True)
print(models[:5])
```

### ① 分類モデル
```python
import torch, timm
model = timm.create_model(
    'resnet18',
    pretrained=True,    # コンペで事前学習禁止なら False
    num_classes=10,     # 出力クラス数（Headを自動で付け替え）
)
out = model(torch.randn(2, 3, 224, 224))
print(out.shape)        # torch.Size([2, 10])
```

### ② 特徴量抽出器（コンペで重要）
```python
fe = timm.create_model('resnet18', pretrained=True, num_classes=0)  # 分類層を除去
feats = fe(torch.randn(2, 3, 224, 224))
print(feats.shape)      # torch.Size([2, 512])  ResNet18は512次元
```

## 代表モデル
| 系統 | 例 | 立ち位置 |
|------|-----|----------|
| ResNet | `resnet18`, `resnet50`, `resnext50_32x4d` | 王道。まずベースライン |
| EfficientNet | `tf_efficientnet_b0_ns`, `efficientnetv2_rw_s` | 低計算量×高精度のコスパ |
| ViT/DeiT | `vit_base_patch16_224`, `deit_base_patch16_224` | パッチ分割のTransformer |
| ConvNeXt | `convnext_tiny`, `convnext_base` | ViT技術を逆輸入した最新CNN |

## Anti-patterns
- **コンペルールを見ずに `pretrained=True`** → 事前学習禁止コンペでは失格・リーク扱い。ルール確認が先。
- **特徴量が欲しいのにHead付きモデルを使い手で剥がす** → `num_classes=0` で一発。手剥がしはバグ源。
- **モデルをゼロ実装** → 時間とバグの無駄。timmで呼ぶ。
- **入力解像度をモデル既定と無確認で使う** → モデルごとに想定解像度がある。`create_model` の `img_size` や前処理を合わせる（解像度調整は [[image_baseline_tuning_kaggle]]）。

## Example
特徴量ベースの追加処理：
```python
fe = timm.create_model('tf_efficientnet_b0_ns', pretrained=True, num_classes=0)
emb = fe(images)            # (B, D) の埋め込み
# → kNN / metric learning / 下流の浅いヘッドに接続
```

## Eval
- `pretrained` がコンペルールに沿っている。
- 分類は `num_classes`、特徴量は `num_classes=0` を使い分けている。
- ベースモデルが ResNet系から始まっている（理由なくViTで重く始めていない）。

## 関連
- [[image_baseline_tuning_kaggle]] — モデル選定・チューニング・解像度の本体
- [[experiment_tracking_wandb]] — model_name を config に記録
- 参考スライド「backbone としての timm 入門」（tawara, 第3回分析コンペLT会）— [[kaggle_learning_resources]]
