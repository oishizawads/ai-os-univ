---
title: "LLM出力の検証（AIを体系的に疑う）"
type: eval_rule
domain: ml
tags: [verification, llm-as-judge, hallucination, eval]
created: 2026-06-18
source:
  title: "Judging LLM-as-a-Judge (arxiv 2306.05685) / Constitutional AI (arxiv 2212.08073)"
  author: "Zheng et al. (NeurIPS 2023), Anthropic"
---

## 原則
「AIと全業務を回す」最大の弱点は**間違いをそのまま信じること**。CLAUDE.mdの"単一経路を信用するな"を、AI出力に対して運用化する。`evaluation_design.md`（モデル評価）とは別レイヤー＝**AI自身の出力の検証**。

## 手法
- **2経路突き合わせ（最優先・低コスト）**: 同じ問いを独立2経路（モデルA/B、またはLLM/検索/計算）で処理し**矛盾を検出**。一致しない箇所だけ人が見る。ハルシネーション検出に直結。
- **LLM-as-Judge（arxiv 2306.05685）**: 強モデルを審査員にopen-ended出力を採点。人手評価なしで品質ゲート。バイアス（位置・冗長性偏好）に注意し基準(rubric)を明示。
- **Constitutional AI 自己批判（arxiv 2212.08073）**: 原則リストを当てて自己修正させる。納品文書の規律チェックに転用可。
- **出典の自己検証**: AIが出した数値・論文ID・「公式」主張は**原典を開くまで信じない**（このセッションで実際にarxiv偽ID/権威偽装が出た）。

## ツール（パイプラインにLLMを入れた段階で）
- **deepeval**（pytest風・LLMシステム単位・忠実性/関連性等／LICENSE要確認）
- **ragas**（RAG専用メトリクス）／ **promptfoo**（プロンプト回帰テスト）

## 判断基準
- クライアント納品にAI生成の数値・引用を載せる → 必ず2経路 or 原典確認。
- LLMを本番分析に組み込む → deepeval等で品質ゲートをCIに。

## 失敗例
- AIの要約・数値を検証せず資料に転記（ハルシネーションを納品）。
- 単一モデルの出力を真として下流処理（誤りが伝播）。
- judgeのrubric未定義で採点がブレる。

関連: [[META_MAP]] ⑤検証層（最重要の穴）/ evaluation_design（モデル評価は別）。
