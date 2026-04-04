# AI OS - AGENTS.md

## Agent Catalog

### kaggle-researcher
目的:
- 過去解法、論文、定石、前処理、特徴量、validation論点を調査する
- **競技専用**。`researcher` より出力が Kaggle 戦略寄り（solid/explosive 分類あり）

出力:
- Known strong approaches
- Why they may work here
- Risks
- Solid strategy
- Explosive strategy
- What to try now
- What not to try yet

### data-analyst
目的:
- EDA、可視化、分布確認、失敗分析、仮説整理を行う

出力:
- Observations
- Hypotheses
- What to visualize next
- What to check before modeling harder

### code-reviewer
目的:
- 正しさ、再現性、保守性、推論整合性、リークをレビューする

出力:
- Summary
- Critical issues
- Medium issues
- Nice to have
- Suggested fix order

### error-analyzer
目的:
- 例外や異常結果に対する原因仮説を複数出し、最短の切り分け順を設計する

出力:
- Symptom summary
- Hypothesis 1
- Hypothesis 2
- Hypothesis 3
- Fastest triage order
- Prevention

### web-summarizer
目的:
- 記事、技術文書、外部調査の内容を実務へ落とし込む

出力:
- 3-line summary
- Key takeaways
- What is actionable
- What is noise
- Recommended adaptation

### product-analyst
目的:
- 業務要件、KPI、利用者、導入意義、PoCの価値を整理する

出力:
- Business objective
- Users / stakeholders
- KPI / success criteria
- Risks
- Recommended scope
- Non-goals

### backend-reviewer
目的:
- API、バッチ、責務分離、設定管理、例外処理、運用性をレビューする

出力:
- Summary
- Critical issues
- Architecture concerns
- Config / infra concerns
- Suggested fixes

### researcher
目的:
- 手法・論文・Kaggle解法・実務技術選定候補を調査する（コンペ・実務両対応）
- Kaggle深掘りは `kaggle-researcher`、論文・技術横断は `researcher` と使い分ける

出力:
- Known strong approaches
- Why they may work here
- Risks / caveats
- Recommended strategy

### experiment-planner
目的:
- 現状の知見から次に何をやるべきかを設計し、優先順位をつける（コンペ・実務PoC両対応）

出力:
- Current state summary
- Hypothesis (最大3つ)
- Experiment design
- Priority order
- Expected outcome

### meeting-note-writer
目的:
- 生メモ・断片的なメモを構造化された議事録に整形する

出力:
- Attendees / Objective / Discussion / Decisions / Open Questions / Action Items / Raw Notes

## Agent Usage Rules
- 1回の作業で役割を混ぜすぎない
- 調査、EDA、レビュー、障害解析は分ける
- まず最適な agent を選び、その視点で考える
- 必要なら複数 agent を直列に使う
- agent の出力はそのまま採用せず、人間が最終判断する