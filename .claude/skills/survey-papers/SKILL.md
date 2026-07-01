---
name: survey-papers
description: 論文や既知解法を調査し、今のプロジェクトで使える形に要約する。
---

# Survey Papers

## Mission
関連研究や既知解法を、いま試す価値のある候補に圧縮する。

## Workflow
1. タスク、評価指標、制約を確認する。
2. 強い既知手法を 3 から 5 件までに絞る。
3. 各手法について `what / why here / risk / try now or later` を整理する。
4. 必要なら `researcher` に補助調査を依頼する。
5. Kaggle 文脈が重要なら `kaggle-researcher` を追加で使う。
6. 今回やる候補と見送る候補を分ける。

## Guardrails
- 論文要約で終わらせず、この案件での意味に落とす。
- 実装コストと validation 影響を無視しない。
- try now は少数に絞る。

## Output
- 3-line summary
- Strong known approaches
- Why they matter here
- Risks / caveats
- Try now
- Try later
- Not worth trying now
