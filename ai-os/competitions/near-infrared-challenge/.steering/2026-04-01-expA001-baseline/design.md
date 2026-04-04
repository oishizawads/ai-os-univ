# design.md

## Hypothesis
まずはシンプルな baseline を作り、そこから前処理・validation の改善余地を評価する方が良い。

## Key Finding from EDA
- trainとtestで樹種(species_number)が完全に非重複
  - train: [1,3,4,5,8,11,12,13,14,15,16,17,19]
  - test:  [2,6,7,9,10,18]
- つまり「未知樹種への汎化」がこのコンペの本質

## Approach

### Validation
- **GroupKFold(n_splits=5, group=species_number)**
- 理由: trainでも1樹種をhold-outすることでtest条件(未知樹種)を模倣できる
- KFoldより現実的なCVになる

### Model
- **Ridge regression** (alpha=1.0)
- 理由: 1555次元の相関した波数列にはL2正則化が有効。シンプルで再現性が高い

### Preprocessing
- **Raw** (前処理なし)
- 理由: baselineは複雑化しない

### Features
- 全波数列(1555本)をそのまま使用
- 列の参照は位置インデックスで行う(日本語列名のエンコード問題を回避)
  - train: col0=sample_number, col1=species_number, col2=tree_species, col3=moisture(target), col4+=wave
  - test:  col0=sample_number, col1=species_number, col2=tree_species, col3+=wave

### Target
- 含水率をそのまま使用(log変換なし)

## Implementation Details

### settings.py
```python
EXPERIMENT_ID = "expA001_baseline"
SEED = 42
N_FOLDS = 5
VALIDATION = "GroupKFold_species"
MODEL_NAME = "Ridge"
PREPROCESSING = "raw"
ALPHA = 1.0
DATA_ENCODING = "cp932"
```

### train.py の流れ
1. train.csv をcp932で読む
2. 列名を位置で rename: sample_number, species_number, tree_species, moisture, wave_0001...
3. wave_cols = col4以降
4. X, y, groups を定義
5. GroupKFold(5) でOOFループ
6. 各foldでRidge fit → OOF predict
7. fold別RMSE + OOF全体RMSE + std を出力
8. 全データでRidgeをfitしてmodel保存(pickle or joblib)
9. OOF予測をCSV保存

### inference.py の流れ
1. test.csv をcp932で読む
2. 同じ列名renameロジック(moisture列なし)
3. 保存済みモデルをload
4. 全testサンプルを予測
5. sample_submit.csv の順序・件数に合わせてsubmission.csv を出力
   - sample_number=95 はtestにあるがsubmitには含まれないので注意

## File Paths (project_root基準)
- 入力: data/raw/train.csv, data/raw/test.csv, data/raw/sample_submit.csv
- モデル保存: experiments/expA001_baseline/model.pkl
- OOF保存:   experiments/expA001_baseline/oof.csv
- 提出ファイル: submissions/expA001_baseline_submission.csv

## Risks
- GroupKFoldの場合、foldによってサンプル数が不均一になる
- alpha=1.0が最適でない可能性がある(baselineなので許容)

## Acceptance Criteria
- train.py が最後まで動いてCV RMSEが出る
- inference.py が動いてsubmissions/に提出ファイルが生成される
- result.md に再現可能な情報が残る