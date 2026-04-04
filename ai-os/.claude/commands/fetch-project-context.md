# fetch-project-context

## Objective
現在のプロジェクトで、着手前に読むべきファイルと把握すべき前提を整理する。

## When to Use
- 新しいセッションの開始時
- プロジェクトを切り替えた時
- 途中で文脈を見失った時
- 他人が触っていたプロジェクトを引き継ぐ時

## Read Order
必ず以下の順で確認する。

### Global
1. `C:/workspace/ai-os/CLAUDE.md` — 運用思想・レビューポリシー
2. `C:/workspace/ai-os/CODEX.md` — Claude/Codex 役割分担
3. `C:/workspace/CLAUDE.md` — agentカタログ・コンテキスト切り替えガイド

### Project Core
4. プロジェクト直下の `CLAUDE.md`
5. `SESSION_NOTES.md`
6. 直近の `.steering/` 配下
7. 直近の `daily_reports/` + `weekly_reports/`

### Competition Project
追加で以下を見る。
- `COMPETITION.md`
- `DATASET.md`
- `METRIC.md`
- `VALIDATION_RULES.md`
- 直近の `experiments/*/result.md`

### Client Project
追加で以下を見る。
- `PROJECT.md`
- `DATA_CONTRACT.md`
- `docs/business_context.md`
- `docs/metrics.md`
- `docs/assumptions.md`
- 直近の `meeting_notes/`

### ZetaX Company Context
追加で以下を見る。
- `work/zetax/COMPANY.md`
- `work/zetax/STRATEGY.md`
- `work/zetax/SESSION_NOTES.md`

## Output Format

### Must Read
- 
- 
- 

### Nice to Read
- 
- 
- 

### Current Objective
現在の目的を3行以内で要約する。

### Current Constraints
- 
- 
- 

### Current Risks
- 
- 
- 

### Immediate Next Action
今すぐやるべき最初の1アクションを書く。

## Hard Rules
- ファイル名を列挙するだけで終わらない
- 「なぜ読む必要があるか」も簡潔に添える
- 情報が競合している場合は、その衝突も明示する