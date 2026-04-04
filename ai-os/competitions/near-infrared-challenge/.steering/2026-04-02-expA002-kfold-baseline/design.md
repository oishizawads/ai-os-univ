# design.md

## Hypothesis
KFold(5)はpublic LBに近いCVを提供し、今後の改善追跡の基準になる。

## 変更点（expA001との差分のみ）
- VALIDATION: GroupKFold_species → KFold_5
- KFold(n_splits=5, shuffle=True, random_state=SEED)
- それ以外は全て同じ（Ridge alpha=1.0, raw, seed=42）

## ファイル構成
expA001_baselineのコードをコピーして変更する。

### settings.py の差分
```python
EXPERIMENT_ID = "expA002_kfold_baseline"
VALIDATION = "KFold_5"
# GROUP_COL は不要（KFoldはgroupsパラメータ不使用）
```

### train.py の差分
```python
from sklearn.model_selection import KFold
splitter = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
for fold, (train_idx, valid_idx) in enumerate(splitter.split(X), start=1):
    # groupsパラメータ不要
```

### inference.py
expA001と同じロジック（モデルパスだけ変わる）

## File Paths
- 実験ディレクトリ: experiments/expA002_kfold_baseline/
- モデル: experiments/expA002_kfold_baseline/model.pkl
- OOF: experiments/expA002_kfold_baseline/oof.csv
- 提出: submissions/expA002_kfold_baseline_submission.csv

## Acceptance Criteria
- train.pyが動いてKFold OOF RMSEが出る（期待値: ~18.6）
- inference.pyが動いて550行の提出ファイルが生成される
- result.mdに記録が残る
