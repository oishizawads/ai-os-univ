# requirements.md — expA005_deriv_corr_pls

## 目的
1次微分前処理 + fold内相関によるTop-N特徴選択 + PLSRegression の組み合わせを検証する。
EDAで1次微分が最大|r|≈0.87と最も有効だったことを受け、特徴選択との組み合わせを試みる。

## 比較対象
- expA004_snv_pls : SNV + PLS + GroupKFold → OOF RMSE 27.85

## 要件
- 前処理 : Savitzky-Golay 1次微分（window=11, polyorder=2, deriv=1）
- 特徴選択 : fold内trainデータの|Pearson r|上位N件（リーク防止のためfold内で計算）
- モデル : PLSRegression
- CV : GroupKFold(n_splits=5, groups=species_number)
- スイープ : N_TOP_FEATURES × N_COMPONENTS の2次元グリッド
- 推論整合 : 最終モデルの選択特徴インデックスをpayloadに保存し、inference.pyで再現する
