---
title: "モデル学習の典型的失敗パターン"
type: failure_pattern
domain: ml
tags: [training, nan, gradient, overfitting, convergence, neural_net]
created: 2026-04-05
---

## パターン1: Loss が NaN になる

**何が起きたか**: 学習開始直後またはある時点でlossがNaNになり学習が止まる。

**根本原因の候補（切り分け順）**:
1. 学習率が大きすぎる → 勾配爆発 → NaN
2. 入力データにNaN・Inf が含まれている
3. log(0) や 0除算が損失計算に含まれている
4. 重みの初期化が不適切

**切り分け手順**:
```
1. 入力データのNaN/Infチェック: df.isnull().any() / np.isinf(X).any()
2. 最初のbatchだけ流してlossを確認
3. 学習率を1/10にして再実行
4. gradient clippingを追加（max_norm=1.0）
5. loss計算にepsilon追加（log(x + 1e-8)等）
```

**再発防止**: 学習前に入力データの sanitize check をルーティン化する。

---

## パターン2: 過学習（train lossは下がるがval lossが上がる）

**何が起きたか**: epochが進むにつれてval lossが上昇し始め、train lossとの乖離が広がる。

**根本原因の候補**:
1. モデルが大きすぎる（パラメータ数 >> データ数）
2. 正則化が不足
3. 学習データが少ない
4. データの多様性が低い（augmentationが足りない）

**切り分け手順**:
```
1. train/val lossをepsilonごとにプロット
2. Early Stoppingを追加して最適epochを確認
3. Dropout / Weight Decay を追加
4. モデルサイズを縮小して比較
5. データ拡張を追加（分類・画像等の場合）
```

**再発防止**: Early Stopping + validation monitoringを最初から入れる。

---

## パターン3: 学習が収束しない（lossが下がらない）

**何が起きたか**: 学習率・バッチサイズを変えても loss が一向に改善しない。

**根本原因の候補**:
1. 学習率が小さすぎる
2. 勾配消失（深いネットワーク・不適切な活性化関数）
3. バッチ正規化が欠けている
4. データの前処理が不適切（スケールが大きい特徴量）
5. ラベルが誤っている

**切り分け手順**:
```
1. 小さいサブセット（100件程度）で意図的に過学習できるか確認
   → できない場合: モデル・データ・ラベルに根本的な問題
   → できる場合: 正則化・データ量の問題
2. Learning Rate Finderで適切な学習率を探索
3. Gradient flowを確認（各層のgradient normをログ）
4. Batch Normalizationを追加
```

**再発防止**: 新しいアーキテクチャを試す前に「小データで過学習できるか」のサニティチェックを実施する。

---

## パターン4: 再現性がない（同じコードで結果が変わる）

**何が起きたか**: 同じコード・同じデータで実行するたびに結果が微妙に変わる。実験の比較ができない。

**根本原因の候補**:
1. シードが固定されていない（Python/NumPy/PyTorch/CUDA）
2. 非決定的なCUDA操作が使われている
3. マルチプロセスのデータロードで順序が変わる
4. 浮動小数点の演算順序の違い

**切り分け手順と対処**:
```python
import random, numpy as np, torch
random.seed(42)
np.random.seed(42)
torch.manual_seed(42)
torch.cuda.manual_seed_all(42)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```

**再発防止**: 実験管理テンプレートにシード設定を必須項目として含める。

---

## パターン5: GPU OOM（メモリ不足）

**何が起きたか**: 学習開始時または途中でCUDA out of memory errorが出る。

**根本原因の候補**:
1. バッチサイズが大きすぎる
2. モデルが大きすぎる
3. gradient accumulation なしに実質的に大きなバッチを使っている
4. 中間activationのメモリが解放されていない

**切り分け手順**:
```
1. バッチサイズを半分にして再実行
2. torch.cuda.memory_summary() でメモリ使用状況確認
3. Mixed Precision Training (fp16) を試す
4. Gradient Checkpointing を使う（速度と引き換え）
5. 不要なテンソルを.detach()/.cpu()で解放
```

**再発防止**: 学習前にダミーの1バッチを流してメモリ確認するスクリプトを用意する。
