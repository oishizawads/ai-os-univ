# requirements.md

## Objective
GroupKFoldが悲観的すぎてCV信頼性が低いため、KFold(5)に切り替えた新しいbaselineを構築する。

## Background
- expA001 GroupKFold OOF=42.44（std=21.78）はfold4の特異樹種（species3,4）に引きずられた
- KFold(5) OOF=18.62（std=1.46）がpublic LB=21.5に最も近い
- 今後の改善追跡はKFold OOFを基準にする

## Success Criteria
- KFold(5) OOF RMSEが計測できる
- 提出ファイルが生成される
- result.mdに再現可能な記録が残る

## Constraints
- モデル・前処理はexpA001と同じ（Ridge alpha=1.0, raw）
- 変更点はCV戦略のみ（KFold shuffle=True seed=42）
- leakage禁止・train/inference整合を崩さない

## Inputs
- data/raw/train.csv, test.csv, sample_submit.csv

## Outputs
- train.py, inference.py, settings.py
- oof.csv, model.pkl
- submissions/expA002_kfold_baseline_submission.csv
