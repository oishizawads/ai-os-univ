---
title: "Model Selection Framework"
type: framework
domain: ds
tags: [model_selection, tabular, time_series, nlp, lgbm, neural_net]
created: 2026-04-05
---

## Summary
モデル選択は「最強のモデルを選ぶ」ではなく「このデータとタスクに合ったモデルを選ぶ」。
まずシンプルなものから始め、データが要求する複雑性だけを追加する。
選択の理由を書けないなら、まだ選んでいない。

## Tabularデータの選択フロー

```
データ量 < 1000件
  → Linear/Ridge/Lasso + 特徴量エンジニアリング重視
  → アンサンブルは過学習しやすいので注意

1000 < データ量 < 10万件
  → LightGBM / XGBoost をデフォルト起点
  → 特徴量エンジニアリングの余地が大きい

データ量 > 10万件
  → LightGBM / CatBoost（カテゴリ変数多い場合）
  → Neural Net（TabNet, FT-Transformer）が有効になり始める

特徴量に強い順序・交互作用がある
  → XGBoost より LightGBM（葉成長）が有効な場合が多い

カテゴリ変数が多い、高カーディナリティ
  → CatBoost

外部事前知識・特徴量設計が難しい
  → Neural Net（特徴量自動学習）
```

## 時系列データの選択フロー

```
系列数 = 1、長期依存なし
  → ARIMA / Exponential Smoothing から始める

系列数 > 1、共変量あり
  → LightGBM（lag特徴量 + rolling特徴量）が現実的に強い

長期依存（数百ステップ以上）
  → Transformer系（TFT, PatchTST, TimesNet）
  → ただし小データでは過学習しやすい

外れ値・欠損が多い
  → Tree系の方がロバスト

点予測より区間予測が必要
  → Quantile regression / Conformal prediction
```

## NLP・テキストの選択フロー

```
ラベルあり、データ > 数千件
  → 事前学習済みBERT系をFine-tuning（日本語: cl-tohoku, rinna等）

ラベルなし / ラベル少量
  → Few-shot with LLM（Claude / GPT）→ 弱ラベル生成 → Fine-tuning

推論速度が優先
  → DistilBERT / TinyBERT / 量子化モデル

文書分類（カテゴリ数 < 20）
  → TF-IDF + LogisticRegression がベースラインとして速い

固有表現抽出（NER）
  → 事前学習済みNER or LLM + プロンプト
```

## モデル比較の共通原則

### やること
- 必ずシンプルなベースライン（線形モデル等）から始める
- 同じCVと評価指標で比較する
- ハイパーパラメータチューニングは最後（アーキテクチャ選択が先）
- 計算コスト・推論速度・メモリも選択基準に入れる

### やらないこと
- 「新しい・有名」という理由だけで選ぶ
- ベースラインより先に複雑なモデルを試す
- 異なるCVで比較する
- チューニングで小さな改善を積み上げてモデル選択を後回しにする

## アンサンブルの選択

| 手法 | 使うとき | 注意 |
|---|---|---|
| 平均（単純） | モデルの多様性が十分あるとき | 最初の選択肢 |
| 加重平均 | CVスコアに差があるとき | 過学習に注意 |
| Stacking | 上位を狙うとき | OOFで必ずvalidate |
| Blending | Stackingの計算コストを下げたいとき | leakageに注意 |

## Eval
- ベースラインより先に複雑なモデルを試していないか
- 同一CVで比較しているか
- 選択理由が「このデータの特性に合っている」と言えるか
- 推論コスト・速度が要件を満たすか
