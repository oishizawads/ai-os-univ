---
title: "Kaggle における Coding Agent / AI の使い方"
type: playbook
domain: ml
tags: [kaggle, ai-agent, coding-agent, claude-code, codex, automation, workflow]
created: 2026-06-05
source:
  title: "LAIME Kaggle Dojo ミーティング横断知見（AI活用）"
  author: "LAIME メンター（石田/村上）＋メンバー"
  isbn: ""
  chapter: ""
---

## Summary
KaggleでのCoding Agent活用に関する現場合意（2026-05時点）。結論は **「コンペ理解・仮説立ては人間、実装と整理はAI」**。
実装の大半をAIに任せても、どこかで頭打ちになり「結局自分で新しく考える所」に到達する。そこは人間がやる前提で、AIを補助に使うのが現実的。アイデア出しAIは（今のところ）あまり効かない。

## Core Principles
- **理解と仮説は人間、量産はAI**。コンペの本質理解・CV設計・仮説立ては人間が担う。AIは実装・要約・候補整理を担う。
- **AIに全部やらせると頭打ち**。定石を出し切ると、タスク固有の工夫＝人間の出番になる。そこを外注しない。
- **アイデア出しAIは過信しない**。前のコンペ・タスク固有の性質は自分で考えた方が良い（現状）。

## Decision Rules
- **AIに任せてよい**：公開Notebook/Discussionの要約、手法候補の整理、定石実装、ボイラープレート、過去コンペ情報の咀嚼。
  - **類似コンペ解法の収集→要約**：`compsearch.dev`（Kaggle解法検索）で類似コンペの上位解法を集め、LLMに「再現しやすいパイプライン」として日本語整理させる。勝ち筋の全体像（前処理/特徴/モデル/アンサンブル/後処理）を素早く掴むのに有効。ただし最終的な取捨選択と自コンペへの適合は人間が判断する。
- **人間がやる**：コンペ理解、CV設計、仮説立て、タスク固有の前処理/後処理の発想、最終判断。
- **本ワークスペースのルーティング**：実装→OpenCode/Gemini、重要レビュー→Codex（節約）、設計・判断→Claude（[[model_routing]]）。Kaggleでも同じ原則＝Claudeは判断、外部は量産。

## Procedure
1. コンペ理解・EDA・仮説は自分でやる（または対話で深める）。
2. discussion/公開NotebookをAIに**要約させ**、手法候補を表に整理させる。
3. 定石・雛形の実装をAIに投げる（[[hydra_experiment_management]] の run.py 雛形など）。
4. AIが提案した定石を**段階的に試す**（一気に全部入れない）。
5. 頭打ちを感じたら、タスク固有の工夫は人間が考える。

## Anti-patterns
- **コンペ理解までAIに丸投げ** → 本質を外し、public overfitや罠に気づけない。
- **アイデア出しをAI頼み** → タスク固有の発想は出てこない。データ解析と人間のアイデア力で勝負（例「画像5ピクセル」の発想）。
- **AI提案を一括投入** → 何が効いたか分からない。段階的に、CVで効果を見る（[[kaggle_experiment_strategy]]）。

## Example
鳥コンペ：discussionをAIに要約させ手法候補を整理 → 自分でCV設計と仮説 → 定石をAIに実装させ段階的にCV評価 → 行き詰まったらタスク固有の前処理を自分で発想。

## Eval
- コンペ理解・CV設計・仮説を人間が担えている。
- AIの提案を段階的にCVで検証している（一括投入していない）。
- 要約・整理など適所でAIを使い、判断を外注していない。

## 関連
- [[model_routing]] — Claudeは判断、外部モデルは量産（WS全体の原則）
- [[kaggle_experiment_strategy]] — 段階的検証・CV中心の回し方
- [[kaggle_medal_strategy]] — discussion全読の土台
