---
title: "Experiment Design for ML"
type: framework
domain: ds
tags: [cv, cross_validation, oof, leakage, validation, experiment]
created: 2026-04-05
---

## Summary
CV設計がモデル選択の全てを決める。
CVがデータの構造を反映していなければ、どんな実験も信頼できない。
まずCVを固定し、そこから動かさない。

## CV戦略の選択

### データ構造ごとの原則
| データ構造 | 推奨CV | 理由 |
|---|---|---|
| IIDサンプル | StratifiedKFold | クラス比率の偏りを防ぐ |
| グループ構造（患者・店舗・ユーザー等） | GroupKFold | グループ内相関によるリーク防止 |
| 時系列 | TimeSeriesSplit / Purged Gap | 未来情報の混入防止 |
| 小データ + 不均衡 | StratifiedKFold + Repeated | 分割の偶然性を減らす |

### CV fold数の選択
- 5-fold: 標準。バランスが良い
- 10-fold: 小データ（<5000件）で使う
- 3-fold: 大データ（>100万件）か計算コストが高い場合
- Leave-One-Out: 極小データのみ。過楽観になりやすい

## OOF（Out-of-Fold）設計原則
- OOFスコアは学習に使われていないデータでの予測 → モデル選択の主要指標
- OOF全体のスコアと各foldのスコア両方を見る（折間ばらつきが大きい = CVが不安定）
- アンサンブルのメタ特徴量にOOFを使う場合、同一CVで作ること（リーク防止）
- OOF予測をチェックせずにPublic LBのスコアだけで判断しない

## リーク防止チェックリスト

### 特徴量リーク（最も多い）
- [ ] ターゲットに依存する集計値（target encoding等）は必ずfold内で計算しているか
- [ ] 時系列データで未来の情報を使っていないか
- [ ] trainとtestで同じ前処理パイプラインが適用されるか（fitはtrainのみ）
- [ ] 外部データにtestのラベルに相当する情報が含まれていないか

### インデックスリーク
- [ ] testデータのIDがtrainに含まれていないか
- [ ] data augmentation後のサンプルが異なるfoldに分かれていないか

### 前処理リーク
- [ ] Scaler・Encoder のfitはtrainのみか
- [ ] 欠損補完にtest情報を使っていないか

## Solid vs Explosive Strategy

### Solidな実験
目的: 安定したベースラインを確保する
基準: CVの標準偏差が小さく、再現性が高い
例: 適切なCV設計 + シンプルな特徴量 + LightGBM

### Explosiveな実験
目的: 上位に食い込むための大きな改善を狙う
基準: 失敗してもSolidな成果を損なわない
例: 外部データ・大規模アンサンブル・NN

### 判断基準
- Solidを固める前にExplosiveをやらない
- ExplosiveはSolidのCVとは別枠で評価する
- Public LBがSolidより高いExplosiveは慎重に（過適合の可能性）

## Anti-patterns
- CVを途中で変える（実験間の比較ができなくなる）
- fold間のスコアを見ずに平均だけ見る
- target encodingをfold外で計算する
- Public LBスコアが上がったという理由だけで採用する
- OOF予測を確認せずに提出する

## Eval
- CVがデータの構造（グループ・時系列・クラス比率）を反映しているか
- fold間のスコアの分散が許容範囲か（±10%以内が目安）
- リーク防止チェックを通過しているか
- OOFスコアとPublic LBスコアの乖離が説明できるか
