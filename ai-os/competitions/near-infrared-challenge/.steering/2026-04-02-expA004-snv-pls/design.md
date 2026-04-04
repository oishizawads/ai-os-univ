# design.md

## Hypothesis
SNVで樹種間スケール差を除去することでPLSの汎化性能が上がり、GroupKFold OOFがRidgeを下回る。

## SNV実装
```python
def apply_snv(X: np.ndarray) -> np.ndarray:
    # X: shape (n_samples, n_features)
    mean = X.mean(axis=1, keepdims=True)
    std  = X.std(axis=1, keepdims=True)
    return (X - mean) / std
```
- サンプルごとに完結するためleakなし
- train/testそれぞれに独立に適用する

## n_components スイープ
候補: [3, 5, 8, 10, 12, 15, 20]
各n_componentsでGroupKFold(5) OOF RMSEを計算。
評価基準: OOF RMSEが低くかつfold stdが小さいものを選ぶ。

## CV
GroupKFold(n_splits=5, groups=species_number)
— KFoldは樹種leakがあるため使わない

## File Paths
- 実験: experiments/expA004_snv_pls/
- モデル: experiments/expA004_snv_pls/model.pkl
- OOF: experiments/expA004_snv_pls/oof.csv
- 提出: submissions/expA004_snv_pls_submission.csv

## train.py 出力イメージ
n_components=  3: GroupKFold OOF=xx.xx  fold_mean=xx.xx  fold_std=xx.xx
n_components=  5: GroupKFold OOF=xx.xx  ...
...
best n_components=XX  OOF RMSE=xx.xx

## 参考値（超えるべき目標）
- Ridge raw GroupKFold OOF: 42.44

## Acceptance Criteria
- スイープ結果が出る（GroupKFold OOF）
- bestモデルで提出ファイル550行が生成される
- result.mdにスイープ結果・best設定・Ridgeとの比較を記録
