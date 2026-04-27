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

## Phase 0.5: Parallel Subagent Launch
コンテキスト読了後、以下を**同時に**起動する。

**researcher** に渡すプロンプト:
```
競技名・タスク種別・評価指標を前提に、強い先行手法・上位解法・定石を調査してください。
出力先: .steering/research.md
観点: CV設計との整合、計算コスト、実装難易度
```

**data-analyst** に渡すプロンプト:
```
train/testの分布・欠損・外れ値・ターゲット相関を分析し、仮説を3つ挙げてください。
出力先: .steering/eda_summary.md
観点: リーク疑惑・fold間ズレ・前処理の必要性
```

両エージェント完了後、`.steering/research.md` と `.steering/eda_summary.md` を読んで矛盾・ギャップを特定してから Phase 1 へ進む。

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