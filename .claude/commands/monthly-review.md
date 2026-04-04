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
- コンペ: `experiment_ledger.csv` または直近の `result.md`
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

## Hard Rules
- Achievements は成果物・数値・決定事項で書く（活動量ではなく）
- Lessons Learned は次回の行動変容に繋がる形で書く
- 中止・保留も必ず記録する（やめた判断が資産になる）
