---
name: experiment-workflow
description: 競技実験を設計、実装、検証、記録まで一貫して進める
---

# Experiment Workflow

## Mission
この skill は、競技用プロジェクトにおいて、再現可能な実験サイクルを回すための標準手順である。

## Phase 0: Read Context
必ず以下を読む。
- `CLAUDE.md`
- `COMPETITION.md`
- `DATASET.md`
- `METRIC.md`
- `SESSION_NOTES.md`
- `VALIDATION_RULES.md`
- 直近の `.steering/`
- 関連する `experiments/*/result.md`

出力:
- Current goal
- Constraints
- Success criteria
- Known risks

## Phase 1: Propose Strategies
最低2案出す。
- Solid strategy: 安定改善狙い
- Explosive strategy: ハイリスク高リターン狙い

各案で示す:
- What changes
- Why it may work
- Risks
- Validation impact
- Implementation cost

最後に、今回採用する案を1つ選ぶ。

## Phase 2: Steering First
コードを書く前に、以下を前提に整理する。
- `requirements.md`
- `design.md`
- `tasklist.md`

最低限書く内容:
- Objective
- Hypothesis
- Files to change
- Risks
- Acceptance criteria

## Phase 3: Implement Carefully
- train / inference の整合を崩さない
- 分割法、seed、前処理、特徴量、モデル設定を明示する
- 重要設定は `settings.py` に寄せる
- 本命コードは `src/`、試作は `ai-src/` を使い分ける

## Phase 4: Validation Mindset
学習前に明示する:
- validation design
- what success looks like
- what failure looks like
- leakage suspicion points
- what to inspect in OOF / fold scores

## Phase 5: Record
実験後は必ず以下を更新する。
- `notes.md`
- `result.md`
- `SESSION_NOTES.md`
- 必要なら `daily_reports/`

`result.md` には最低限以下を書く。
- Experiment ID
- Objective
- Validation
- Seed
- Model / preprocessing
- Fold scores
- Mean / std
- Findings
- Failure modes
- Next hypothesis

## Output Format
- Goal
- Candidate strategies
- Selected strategy
- Files to change
- Risks
- Validation plan
- Record plan
- Go / No-go judgment