---
title: "TimesFM: Time Series Foundation Model"
type: framework
domain: data-science
tags: [forecasting, time-series, foundation-model, google]
created: 2026-05-03
source: "https://github.com/google-research/timesfm"
---

## Summary
Google Researchによる、ゼロショット時系列予測のための学習済みデコーダー専用トランスフォーマーモデル。
多様な時系列データで事前学習されており、追加学習なしで高精度な予測が可能。

## Core Principles
- **Zero-Shot Capability**: 特定のドメインに依存せず、未知のデータに対しても即座に予測を行う。
- **Decoder-Only Architecture**: 時系列をトークン列として扱い、トランスフォーマーのデコーダー構造で次の値を予測する。
- **Quantile Forecasting**: 単一点の予測だけでなく、分位点（Quantile）による不確実性の推計をサポート。

## Procedure
1. **Setup**: `uv` などのパッケージマネージャーで依存関係（PyTorch/Flax）をインストール。
2. **Model Loading**: Hugging Face から学習済み重みをロード。
3. **Configuration**: `ForecastConfig` を定義（Context Length, Horizon, Normalization等）。
4. **Execution**: 時系列データを入力し、`model.forecast()` で将来値を生成。

## Actionable Insights
- **Data DS Integration**: 従来の統計手法（ARIMA/Prophet）の代わりに、まず TimesFM でゼロショットのベースラインを構築する。
- **Long Context Usage**: モデルの文脈長（最大16k）を活かし、長期間のトレンドと季節性を同時に捉える。
- **Validation**: 量子化予測を利用し、信頼区間の広い期間についてはモデルの判断を慎重に扱う。
