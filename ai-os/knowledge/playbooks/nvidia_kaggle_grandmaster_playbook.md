---
title: "NVIDIA Kaggle Grandmaster Playbook"
type: playbook
domain: ds
tags: [kaggle, competition, ensemble, GPU, LLM-agent, stacking, pseudo-label]
source:
  - https://developer.nvidia.com/blog/winning-a-kaggle-competition-with-generative-ai-assisted-coding/
  - https://developer.nvidia.com/blog/the-kaggle-grandmasters-playbook-7-battle-tested-modeling-techniques-for-tabular-data/
created: 2026-05-03
---

## Summary
NVIDIAが公開した2本の記事から抽出した実戦手法。
「3 LLMエージェントで1位」記事 + 「Grandmaster の7手法」記事の統合。
GPU加速 × 大量実験 × 多段アンサンブルが現代コンペの勝ちパターン。

---

## Part 1: AI支援コーディングで1位を取った戦略

### 体制
- GPT-5.4 Pro / Gemini 3.1 Pro / Claude Opus 4.6 を**並行**稼働
- 60万行のコード生成・850回の実験 → テレコムチャーン予測コンペ優勝

### 4フェーズ × プロンプトパターン

| フェーズ | 目的 | プロンプト例 |
|---------|------|------------|
| EDA | データ構造・分布シフト把握 | 「train.csv と test.csv を探索するEDAコードを作成・実行して」 |
| ベースライン | 複数モデルを並行生成 | 「kfold XGBoostパイプラインの完全コードを作成して」 |
| 特徴量 | 反復的な置換・追加 | 「XYZをABCの代わりに使う完全な置換コードを作成して」 |
| アンサンブル | 150モデルを4層スタックに統合 | hill climbing + Ridge/NN/GBDTのメタモデル |

### 重要な実装原則
- **全実験結果を保存する**: 予測値をNumpy形式で蓄積 → 知識蒸留で後続モデルに転移
- **GPU加速必須**: cuDF / cuML でデータフレーム操作とモデル訓練を高速化
- **並列エージェント**: 複数LLMに同じ問題を同時に解かせて多様性を確保

---

## Part 2: Grandmaster の7つのタブラーデータ手法

### 前提: 2つの基盤
1. **高速な実験**: GPU加速（cuDF, cuML, XGBoost/LightGBM/CatBoostのGPU版）でサイクルを短縮
2. **厳密な検証**: k-fold。時系列→TimeSeriesSplit、グループデータ→GroupKFold。テストの構造に合わせる

### 7手法

#### 1. スマートなEDA
単なる基本チェックを超える。
- 訓練・テストの**分布シフト検出**（本番での失敗を事前に防ぐ）
- 目的変数の**時間的パターン**を確認

#### 2. 多様なベースライン
単一モデルに依存しない。
- 線形モデル・GBDT・NNを**並行評価**
- 各モデルファミリーの適性を序盤で判定

#### 3. 大規模特徴エンジニアリング
- カテゴリ組み合わせなど**数百〜数千の特徴**を生成
- cuDFのgroupby・集計・エンコーディングで高速化（従来月単位→日単位に）

#### 4. ヒルクライミング
- **最強単一モデルから開始**し、異なる重みの組み合わせを段階的に試行
- CuPyで複数評価指標を並列計算
- ブレンドの出発点として使う

#### 5. スタッキング（OOF）
- 第1段階の**OOF予測を第2段階の入力特徴**として使用
- 複雑なパターンを多段階で捉える
- リーク防止: 必ずOOF（Out-Of-Fold）で生成すること

#### 6. 疑似ラベリング
- 未ラベルデータに最強モデルの予測を付けて訓練データに組み込む
- **ソフトラベル（確率値）を使う**（ハードラベルより安定）
- 複数ラウンド反復可能
- k-fold時のリークプロテクション必須

#### 7. 追加訓練
- **複数の異なるランダムシード**でモデルを訓練（シードアンサンブル）
- 最終的に**全データで再訓練**
- わずかだが確実な性能向上

---

## 手法の組み合わせパターン（上位帯の典型）

```
EDA（分布シフト確認）
  ↓
多様なベースライン（GBDT + NN + 線形）
  ↓
大規模特徴エンジニアリング（cuDF高速）
  ↓
ヒルクライミングで最良ブレンドを探索
  ↓
スタッキング（OOF予測を特徴として使用）
  ↓
疑似ラベリングで未ラベルデータを活用
  ↓
複数シード + 全データ再訓練
  ↓
最終アンサンブル
```

---

## このワークスペースへの適用

| 手法 | 対応ツール |
|------|-----------|
| 並列LLMエージェント | `parallel_agent_workflow.md` + `/codex:rescue` + `/gemini-coder` |
| GPU加速実験 | cuDF / cuML（FinceptTerminalのQuantLibも活用可） |
| 実験記録 | メトリクス=WandB / 意図・採用判断・次仮説=`result.md` |
| 知識蒸留（予測値の蓄積） | `result.md` + OOFをnpyで保存する規約 |
| EDA | `/eda` コマンド + `data-analyst` agent |

## Anti-patterns（記事から）
- 単一モデルにフォーカスして実験の多様性を失う
- Public LBだけで採用判断する
- OOFを使わずスタッキングしてリークを起こす
- 疑似ラベルにハードラベルを使って訓練が崩れる
