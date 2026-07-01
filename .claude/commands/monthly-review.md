# monthly-review

## Objective
1ヶ月の活動を振り返り、月次レポートを作成する。学びと方針を整理する。

## When to Use
- 月末または月初
- 四半期・半期評価の前

## Process

### Step 1: 今月の活動を収集
以下を読む。
- 今月分の `weekly_reports/YYYY-Www.md`
- 今月分の `daily_reports/`（週次がない場合）
- `SESSION_NOTES.md` の今月分
- コンペ: 直近の `result.md`（意図・採用判断・次仮説）と WandB の run 履歴（メトリクス）
- 実務: 提案書・PoC資産・`STRATEGY.md` の変化

### Step 2: 月次レポートを作成
`monthly_reports/YYYY-MM.md` に以下フォーマットで書く。

```markdown
# Monthly Report - {year}-{month:02d}

## Theme
今月を一言で表す。

## Achievements
- 

## Metrics / Results
| 指標 | 値 | 前月比 |
|------|-----|--------|
|      |     |        |

## Experiments / Projects
### 完了
- 
### 継続
- 
### 中止・保留
- 

## Lessons Learned
-

## Strategy Update
方針変更・新たな知見があれば記録する。
-

## Next Month Goals
1. 
2. 
3. 
```

### Step 3: 中長期の方針ファイルを更新
- コンペ: `SESSION_NOTES.md` に月サマリを追記
- 実務: `STRATEGY.md` や `internal_docs/` を必要に応じて更新

### Step 4: ワークスペース自己監査（死蔵の炙り出し）
- `python tools/usage_meter.py` を実行（continuous-learning の既存観測ログから tool/skill/agent の実使用頻度を集計・読み取り専用・新規計測なし）。
- 数週間の蓄積を前提に、観測期間を通して **0回の skill/agent** は整理候補に挙げる（即削除でなく要確認。1〜2週では "未使用" ≠ "死蔵"）。
- 余力があれば `context-budget` スキルで常時コンテキストの増分も測る。

## Hard Rules
- Achievements は成果物・数値・決定事項で書く（活動量ではなく）
- Lessons Learned は次回の行動変容に繋がる形で書く
- 中止・保留も必ず記録する（やめた判断が資産になる）
- skill/agent の整理は `usage_meter.py` の実測に基づく（推測で切らない）。削除は git 管理下で可逆に
