# requirements.md

## Objective
近赤外コンペの信頼できる baseline を構築する。

## Success Criteria
- baseline が最後まで train / inference 一貫で動く
- validation 条件が明示されている
- result.md に再現可能な情報が残る

## Constraints
- 複雑化しない
- leakage 禁止
- public LB 最適化をしない

## Inputs
- train.csv
- test.csv

## Outputs
- baseline 学習コード
- 推論コード
- result.md

## Non-goals
- 高度なアンサンブル
- 深層学習