---
name: causal-inference
description: 因果効果を推定・評価・伝える分析タスクで使う。識別戦略の選定、推定、診断、感度分析、レポートまでをガイドする。
---

# Causal Inference

## Mission
「相関」と「因果」を区別し、観察データまたは実験データから政策・施策・機能変更の効果を再現可能に推定する。

## When to Use
- 施策の効果測定（AB テスト以外、もしくは AB テストの代替設計）
- 観察研究での処置効果推定
- どの変数が媒介・修飾しているか調べたい
- 反実仮想（what-if）の推論が必要
- 効果測定 / アナリティクス領域で因果解釈が求められる

## Read Context
最初に読む:
- `CLAUDE.md`
- `SESSION_NOTES.md`
- プロジェクトの `DATASET.md`, `VALIDATION_RULES.md`（あれば）
- 既存の `.steering/` や決定ログ
- 観察データの場合は `data_dictionary` / `schema`

## Workflow

### 1. Estimand を定義
- 処置変数 T、結果変数 Y、ターゲット集団を明確にする
- ATE / ATT / CATE / LATE / 媒介効果 などを選ぶ
- ビジネス問いに直結する形で書く

### 2. 識別戦略を選ぶ
候補を列挙し、データと仮定の強さで選定:

| 戦略 | 必要な仮定 | 使いどころ |
|---|---|---|
| RCT / AB | ランダム化 | 実験可能な場合は第一選択 |
| 傾向スコア（IPW / マッチング / 層別） | 条件付き独立性 | 観察データ、交絡変数観測可能 |
| 回帰不連続（RD） | 閾値近傍の連続性 | 閾値に基づく処置割り当て |
| 操作変数（IV / 2SLS） | 除外制約・関連性 | 処置が内生的 |
| 差分の差分（DiD） | 平行トレンド | パネルデータ、政策導入 |
| 構造因果モデル / do-calculus | 因果グラフが正しい | 複雑な交絡や媒介を可視化 |
| ML 系 CATE | SUTVA・CIA など | 異質性効果、EconML / CausalML |

### 3. データ・仮定診断
- 共変量バランス（SMD、LOVE plot）
- 支持領域（common support）チェック
- 平行トレンドの可視化（DiD）
- 因果グラフの妥当性レビュー（DAG）
- SUTVA / positivity / no unmeasured confounding を列挙

### 4. 推定
- 基本統計量 → 推定器選択 → フィット → 信頼区間取得
- 必要なら重み付け、共変量調整、クラスター頑健標準誤差
- 推定器: statsmodels / linearmodels / econml / causalml / dowhy

### 5. 感度分析・ロバストネス
- 未観測交絡の影響（Rosenbaum bounds、E-value、omitted variable bias）
- 異なる推定器・サンプル定義での比較
- Placebo test、leave-one-covariate-out

### 6. 不確実性が高いら decision-lab
以下のときは decision-lab で複数経路を並列検討する:
- 識別戦略が複数候補ある
- 仮定の破れやすさが大きい
- 推定結果の解釈が事業判断に大きく影響

### 7. 記録・伝える
`result.md` または `decisions/` に以下を残す:
- estimand / identification / data / estimator
- diagnostics / sensitivity / conclusion / next hypothesis

可視化: 効果量 ± 信頼区間、CATE プロファイル、平衡プロット
因果解釈の限界を必ず書く

## Output
- Estimand
- Identification strategy and assumptions
- Data checks (balance / support / trends)
- Estimation result with CI
- Sensitivity / robustness summary
- Limitations
- Decision recommendation

## Recommended Tools
本ワークスペースで検討済みの主要ライブラリ（2026-06-22 時点）:

| 用途 | ライブラリ | URL |
|---|---|---|
| 統合フロー（識別 → 推定 → 反証） | DoWhy | https://github.com/py-why/dowhy |
| ML系 CATE / DML / Causal Forest | EconML | https://github.com/py-why/EconML |
| Uplift modeling / CATE | CausalML | https://github.com/uber/causalml |
| 準実験デザイン（DiD / SC / RD / ITS） | CausalPy | https://github.com/pymc-labs/CausalPy |
| Double Machine Learning | DoubleML | https://github.com/DoubleML/doubleml-for-py |
| Panel / IV / 2SLS / GMM | linearmodels | https://github.com/bashtage/linearmodels |
| DAG / SCM / 因果発見 | pgmpy | https://github.com/pgmpy/pgmpy |
| R: Causal Forest / IV Forest | grf | https://github.com/grf-labs/grf |

注意: `quantumblacklabs/causalnex` は現在使用不可（リポジトリが改ざんされている）。

## Guardrails
- 「相関＝因果」と言わない
- 識別戦略を決める前に推定器を回さない
- 仮定を黙って置かない → 必ず列挙して可視化/検証
- 交絡変数が観測できているかを疑う
- 推定値だけでなく、どれだけ頑健かを報告
- 必要に応じて decision-lab を挟む
