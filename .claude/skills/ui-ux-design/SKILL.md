---
name: ui-ux-design
description: 画面・ダッシュボードの情報設計の正典（オンデマンド）。何をどう配置し何のチャートを使うかを決める。実装は frontend-build へ委譲、仕上げは ui-polish。
---

# UI/UX Design

## Mission
「何を作るか」を決める層。クライアント向けダッシュボード/デモの情報設計・画面構成・UX を、DS の中身が伝わる形に落とす。手を動かす前の設計が役割。

## Rules
- **目的とユーザーを先に**: 誰が・何を判断するために見るか。意思決定に効く数字を主役にする（[[work-implementation]] の利用者/KPI 確認と接続）。
- **1画面1メッセージ**: その画面で言いたいことを1つに。補助情報は従属させる。
- **情報階層**: 概要→詳細のドリルダウン。トップに結論KPI、下に内訳。
- **チャート選択**: 比較=棒 / 推移=折れ線 / 構成=積み上げ or 帯 / 関係=散布 / 地理=地図。**配色・y軸ルールは [[viz-style]]**（jet/rainbow禁止・棒は0起点）。迷ったら下記DBを引く。
- **入力と結果の対応**: ダッシュボードなら「操作（フィルタ/シナリオ）→ 何が変わるか」を明確に。MTJ系のWhat-if比較はこの型。
- **最小から作る**: いきなりリッチにしない。骨格→検証→肉付け。

## チャート選択DB（vendored・オンデマンド）
- **`references/chart-selection.csv`**（25種・vendored from nextlevelbuilder/ui-ux-pro-max-skill, MIT）: データ型→最適チャート→2次候補→使う条件→**使うな条件**→データ量閾値→色指針→a11yグレード→フォールバック→ライブラリ。**チャートを迷ったら必ずこれを引く**（viz-styleは配色/y軸ルール、こちらは"選択"の判断）。
- カバー: Trend/Compare/Part-to-Whole/Correlation/Heatmap/Geo/Funnel/Forecast/Anomaly/Hierarchical/OHLC/Distribution/Process Mining 等、DS分析に直結。
- さらに深い設計（BIダッシュボードUX・スライドレイアウト/配色DB）が要るときは上流リポジトリの `design-system/data/slide-*.csv` を引く（導入前に中身をvet・[[safe-data-handling]]）。常時ロードしない。

## Workflow
1. 目的・ユーザー・判断したい問いを1行で書く。
2. 画面構成（主役KPI→内訳→操作）をワイヤーで決める。
3. チャートを選ぶ（`references/chart-selection.csv` で型→最適チャート＋"使うな"条件を確認 → 配色/y軸は [[viz-style]]）。
4. 仕様を [[frontend-build]] に渡して実装を委譲。
5. [[ui-polish]] で仕上げ、[[ship-harden]] で堅牢化。

## Guardrails
- **見栄えより伝達**。装飾は二の次、まず「正しく速く理解できるか」。
- 設計を自分でやり、実装はエージェントに委譲してよい（君は判断者）。
- クライアント文書の表現規律（実証を装わない等）はUI内テキストにも適用（[[stop-slop]]）。
