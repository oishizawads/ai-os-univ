# Near Infrared Challenge - CLAUDE.md

## Goal
このプロジェクトは、木材スペクトルから含水率を予測する競技用実験リポジトリである。
目的は、CV再現性を保ちながら、解釈可能で筋の良い改善を積み上げること。

## Principles
- CVが不安定な案は本命にしない
- 再現できない実験は価値が低い
- public LBだけで判断しない
- 前処理とvalidationを先に詰める
- いきなり深層学習に飛ばない
- baselineとの差分で改善を判断する
- solid strategy と explosive strategy を分けて考える

## Read First
1. `COMPETITION.md`
2. `DATASET.md`
3. `METRIC.md`
4. `SESSION_NOTES.md`
5. `VALIDATION_RULES.md`

## Directory Rules
- `src/` は本命の整理されたコード
- `ai-src/` はAIによる試作や叩き台
- `experiments/expAxxx_*` はClaude主導
- `experiments/exp2xx_*` は人間主導

## Experiment Rules
- 実験前に `.steering/` を作る
- `requirements.md`, `design.md`, `tasklist.md` を前提に進める
- 実験後は `notes.md`, `result.md`, `SESSION_NOTES.md` を更新する
- train / inference の整合を崩さない
- seed と validation を明記する

## Review Rules
- 実装後は `review-exp` 観点で見直す
- リーク、推論不整合、seed漏れ、設定散乱を重点確認する