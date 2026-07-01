---
title: "Kaggle 学習リソース集（書籍・スライド・記事・リポジトリ）"
type: reference
domain: ml
tags: [kaggle, resources, books, references, tools]
created: 2026-06-05
source:
  title: "LAIME Kaggle Dojo 共有リンク集（2025-2026）"
  author: "LAIME メンバー/メンター共有"
  isbn: ""
  chapter: ""
---

## Summary
LAIME Kaggle Dojo で共有された、コンペ運用に役立つ教材・資料のポインタ集。手法の詳細は各フレームワークに、ここは「どこを見るか」の索引。

## 書籍（kami 推奨）
- **Kaggleで勝つデータ分析の技術** — 古いがバイブル。バリデーションの考え方など全コンペ共通の要素。脇に置いて読み返す一冊。
- **目指せメダリスト！Kaggle実験管理術** — スコアを直接上げる本ではなく「どう取り組むか」の示唆（村上寄稿）。
- **Kaggleではじめる大規模言語モデル入門** — NLP/LLM特化のKaggle本。GPUリソース要（村上寄稿）。

## スライド / 発表
- **backbone としての timm 入門（tawara、第3回分析コンペLT会）** — timm の定番解説（[[timm_usage]]）。
- **画像コンペ入門（charm、ML_Bear 雑メモ経由）** — 実戦的。「これだけでいい、他は試さない」系の取捨選択。pytorch-lightning 使用。
- **Pythonパッケージ管理 [uv] 完全入門（mickey_kubo）** — ローカル環境は uv 推奨（Rust製・高速）。[[python-ops]] と整合。
- **Agent時代のKaggleで人間は何を見るべきか（中山、関西Kaggler会 2026.5）** — [[ai_agents_in_kaggle]] の背景。
- ** MLコンペ実験テンプレを作ろう（unonao/kami）** — [[hydra_experiment_management]] のテンプレ元。

## 記事
- **Claude Code / CodexでKaggle金メダルを取った話（Zenn, chiman）** — AI活用の価値。[[ai_agents_in_kaggle]]。
- **NVIDIA GM Playbook（テーブル7技法 / 生成AI支援コーディング）** — [[nvidia_kaggle_grandmaster_playbook]]。
- **Why re-use training parameters to transform test data?（Sebastian Raschka）** — 正規化は train で fit→test を transform。リーク防止の基本（[[kaggle_experiment_strategy]]）。

## リポジトリ
- **unonao/kaggle-template** — メジャー/マイナー版管理のテンプレ（[[hydra_experiment_management]]）。
- **unonao/atmacup11** — 画像コンペ実装の参考。
- **surumenDD/kaggle-discussion-setting-template** — discussion知識ベースのテンプレ（本WSの `/kaggle-discussion-setup` 系の元）。

## ツール
- **uv** — Pythonパッケージ/環境管理（docker より手軽との声）。
- **Kaggle MCP** — datasets を自然言語で操作。
- **Readable** — PDF翻訳（論文読解が激安で便利）。
- **compsearch.dev** — Kaggle解法検索。類似コンペと上位解法を素早く見つける（[[ai_agents_in_kaggle]] の解法収集→LLM要約に）。
- **Papers With Code** — タスク別のSOTAモデル/論文を調べる。
- **lightly** — 画像SSLライブラリ（SimSiam等）。import は `from lightly.data import LightlyDataset` のようにクラスを直接（バージョンで `__init__.py` の自動読込が変わる点に注意）。
- **DINO / DINOv2 / DINOv3** — contrastive な事前学習で人気（[[ssl_pseudo_label_kaggle]]）。

## 関連
- [[kaggle_medal_strategy]] / [[kaggle_experiment_strategy]] / [[ai_agents_in_kaggle]]
