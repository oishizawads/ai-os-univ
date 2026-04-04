# design.md

## Hypothesis
PLSはRidgeより1555列の相関構造を効率よく使えるため、OOF RMSEが改善する。

## Approach

### n_components スイープ
候補: [5, 10, 15, 20, 25, 30, 40, 50]
各n_componentsでKFold(5) OOF RMSEを計算して比較する。
best n_componentsを選び、全データで再学習して最終モデルとする。

### モデル
sklearn.cross_decomposition.PLSRegression(n_components=n, max_iter=500)
予測値は predict() で shape (n,1) が返るので ravel() すること。

### CV
KFold(n_splits=5, shuffle=True, random_state=42) — expA002と同じ

### Preprocessing
raw（前処理なし）— expA002と同じ

## 差分（expA002との変更点）
- Ridge → PLSRegression
- n_componentsのスイープを追加
- ALPHA → N_COMPONENTS（settings.py）

## File Paths
- 実験ディレクトリ: experiments/expA003_pls/
- モデル: experiments/expA003_pls/model.pkl
- OOF: experiments/expA003_pls/oof.csv
- 提出: submissions/expA003_pls_submission.csv

## Output in train.py
各n_componentsのOOF RMSEを表示し、最良を選択。例:
  n_components=  5: OOF RMSE=xx.xx
  n_components= 10: OOF RMSE=xx.xx
  ...
  best n_components=XX  OOF RMSE=xx.xx

## Acceptance Criteria
- スイープ結果が出る
- best n_componentsで最終モデルを保存
- 提出ファイル550行が生成される
- result.mdにスイープ結果とbest設定を記録
