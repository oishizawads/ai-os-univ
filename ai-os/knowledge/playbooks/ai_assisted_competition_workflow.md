---
title: "AI-Assisted Competition Workflow"
type: playbook
domain: ds
tags: [kaggle, competition, LLM-agent, AutoKaggle, AgentK, HEBO, workflow]
sources:
  - https://developer.nvidia.com/blog/winning-a-kaggle-competition-with-generative-ai-assisted-coding/
  - https://arxiv.org/html/2410.20424v3  # AutoKaggle ICLR 2025
  - https://artgor.medium.com/paper-review-large-language-models-orchestrating-structured-reasoning-achieve-kaggle-grandmaster-4ff8ab49deea
  - https://mlcontests.com/state-of-machine-learning-competitions-2025/
created: 2026-05-03
---

## Summary
2025-2026年のKaggle上位解法・論文から抽出したAI支援ワークフローの実践知。
Claude（司令塔）+ OpenCode/Gemini（実装）+ decision-lab（分析）の体制に直接適用可能。

---

## 1. フェーズロック・ワークフロー（AutoKaggle / ICLR 2025）

フェーズを**厳密に分離**することでバグ特定とデバッグ速度が上がる。
フェーズをまたいで汚染しない。

```
Phase 1: Background Understanding
  → コンペ説明・ルール・評価指標を読む
Phase 2: Preliminary EDA
  → データ形状・型・欠損・目的変数分布
Phase 3: Data Cleaning
  → 欠損処理・型変換・外れ値
Phase 4: In-depth EDA
  → 分布シフト・特徴量間相関・時間パターン
Phase 5: Feature Engineering
  → 新特徴量生成（下記11関数チェックリスト参照）
Phase 6: Modeling / Validation / Prediction
  → CV・ハイパラ最適化・アンサンブル
```

各フェーズ終了時にチェックポイントを設け、次フェーズへ持ち込む情報を明文化する。

### 特徴量エンジニアリング 11関数チェックリスト
- [ ] OneHotEncode
- [ ] FrequencyEncode
- [ ] TargetEncode
- [ ] CorrelationFeatureSelection
- [ ] ScaleFeatures
- [ ] PolynomialFeatures（2次交互作用）
- [ ] GroupBy集計（mean/std/min/max）
- [ ] LagFeatures（時系列の場合）
- [ ] RankTransform
- [ ] BinaryFeatureInteraction
- [ ] DomainSpecific（タスク固有の変換）

### LLMエージェントへの指示原則（AutoKaggle）
- Planner: 1フェーズ最大4タスクまで（過負荷防止）
- Developer: 自己修正ループ**上限5回**（無限リトライ禁止）
- Reviewer: 論理的正しさのユニットテストを必須（構文チェックだけでは不十分）
- **速いモデルを使う**: 反復コード生成にはo1系より GPT-4o / Claude Sonnet が有効（推論オーバーヘッドがボトルネック）

---

## 2. 実験ファクトリーの設計（NVIDIA）

### OOF・テスト予測の保存規約
```python
# 命名規約: train_oof_[MODEL]_[VERSION].npy
np.save(f"train_oof_{model_name}_v{version}.npy", oof_preds)
np.save(f"test_{model_name}_v{version}.npy", test_preds)
```
全実験を保存 → 後からhill climbingで最良アンサンブルを探索できる。
**捨てない。後で使う。**

### 並列エージェント体制
```
[Claude]  → 実験設計・結果判断・採用可否
[OpenCode] → 実装・実行（デフォルト）
[Gemini]  → 別実装・コード検索・フォールバック
```
同じタスクを複数エージェントに並行させると多様性が生まれ、アンサンブル候補が増える。

---

## 3. ハイパーパラメータ最適化（Agent K）

**HEBO（Heteroscedastic Evolutionary Bayesian Optimization）** を使う。
OptunaよりAgent Kが採用した実績あり。

```bash
pip install HEBO
```

```python
from hebo.design_space.design_space import DesignSpace
from hebo.optimizers.hebo import HEBO

space = DesignSpace().parse([
    {'name': 'learning_rate', 'type': 'num', 'lb': 1e-4, 'ub': 1e-1},
    {'name': 'max_depth', 'type': 'int', 'lb': 3, 'ub': 12},
    {'name': 'n_estimators', 'type': 'int', 'lb': 100, 'ub': 2000},
])
opt = HEBO(space)
for i in range(50):
    rec = opt.suggest(n_suggestions=1)
    score = evaluate(rec)   # CV score
    opt.observe(rec, np.array([[score]]))
```

---

## 4. ソリューションライブラリの構築（Agent K）

コンペ終了後に**再利用可能なコードを抽出してタグ付け保存**する。
これが「記憶」になり、次のコンペでの立ち上がりを高速化する。

保存先: `ai-os/knowledge/snippets/` または `ai-os/shared/snippets/`

タグ例:
```
competition_type: tabular / nlp / cv / time-series
data_modality: structured / text / image / multi-modal
task_type: classification / regression / ranking
technique: target-encode / pseudo-label / stacking / oof-blend
```

### 失敗の構造化記録（META-ERROR-THOUGHT）
失敗した実験には必ず記録する:
```
何が失敗したか:
どのフェーズで起きたか:
何を変えたか:
なぜ失敗したと思うか:
次に試すこと:
```
→ `ai-os/knowledge/failure_patterns/` に追記

---

## 5. 2025年コンペのメタトレンド（mlcontests.com）

| 領域 | 勝ちパターン |
|------|------------|
| タブラー | XGBoost + LightGBM + CatBoost の3種すべて試す（どれが勝つかはデータ次第）|
| NLP/テキスト | **Qwen2.5 をベースラインに**（2025年の勝ちモデル） |
| ファインチューニング | **Unsloth**（訓練）+ **vLLM**（推論）でHuggingFace比で大幅高速化 |
| 合成データ | 生成→訓練→予測→疑似ラベル→再訓練のループを複数ラウンド |
| チーム規模 | 2025年勝者の50%以上がソロ。チーム規模より**計算資源**が差別化要因 |

---

## 6. 優先度別 実装ロードマップ

| 優先度 | 手法 | 工数 | 期待効果 |
|--------|------|------|---------|
| 🔴 高 | OOF+テスト予測を`.npy`で全保存 → 終盤にhill climbing | 低 | アンサンブルの質 |
| 🔴 高 | フェーズロック（6フェーズ明示的分離） | 低 | デバッグ速度 |
| 🟡 中 | HEBO でハイパラ最適化（Optuna代替） | 低 | スコア |
| 🟡 中 | ソリューションライブラリの構築開始 | 中 | 将来のコンペ速度 |
| 🟡 中 | 合成データ + 疑似ラベルループ | 中 | 低データ問題のスコア |
| 🟢 低 | 3エージェント並列コード生成 | 高（セットアップ） | 実験ボリューム |

---

## このワークスペースへの適用

```
コンペ開始
  ↓
/fetch-project-context → CLAUDE.md + SESSION_NOTES.md 読み込み
  ↓
Phase 1-2: /eda コマンド + data-analyst agent
  ↓
Phase 3-4: Claude が分布シフト確認・CV設計
  ↓
Phase 5: /opencode-coder で特徴量生成（11関数チェックリスト）
  ↓
Phase 6: 全OOFを .npy で保存 → HEBO でハイパラ最適化
  ↓
アンサンブル: hill climbing → スタッキング → 疑似ラベリング
  ↓
/submit でチェック → メトリクスは WandB、意図・採用判断・次仮説は result.md に記録
  ↓
コンペ後: ソリューションライブラリへ抽出
```
