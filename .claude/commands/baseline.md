# baseline

## Objective
信頼できる baseline を設計し、以後の改善の比較基準を作る。

## When to Use
- 新しいコンペを始めた時
- 新しい案件データで最初のモデルや分析を作る時
- モデルが複雑化しすぎた時に立ち返る時

## Baseline Principles
- まず動くこと
- まず再現できること
- まず比較軸になること
- まだ凝らないこと

## Required Decisions
必ず以下を明示する。
- objective
- target
- id handling
- validation
- seed
- preprocessing
- model
- inference parity
- record location

## Output Format

### Baseline Objective
-

### Minimal Setup
- target:
- features:
- preprocessing:
- model:
- validation:
- seed:

### Why This Baseline Is Trustworthy
- 
- 
- 

### What Not to Optimize Yet
- 
- 
- 

### Expected Outputs
- train script
- inference script
- result record
- experiment ID

### First Improvement Candidates
1. solid:
2. solid:
3. explosive:

## Hard Rules
- baseline で複雑な feature engineering をしない
- validation を曖昧にしない
- train / inference の整合を最初から意識する
- baseline の目的は「最強」ではなく「比較基準」