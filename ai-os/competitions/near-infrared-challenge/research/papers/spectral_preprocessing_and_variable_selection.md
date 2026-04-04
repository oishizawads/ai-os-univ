# Spectral Preprocessing And Variable Selection

## Scope

NIR/Vis-NIR スペクトル回帰で、前処理と波長選択がどう効くかを整理する。

## Key Sources

### 1. Vis-NIR Spectroscopy and PLS Regression with Waveband Selection for Estimating the Total C and N of Paddy Soils in Madagascar

- URL: https://www.mdpi.com/2072-4292/9/10/1081
- Accessed: 2026-04-02
- Relevance: スペクトル回帰における波長選択の代表例

What seems useful here:

- VIP ベースで重要波長を絞る考え方が有効
- 今の「相関上位100本」は簡易版の波長選択と見なせる

### 2. Visible and Near-Infrared Spectroscopy with Multi-Parameters Optimization of Savitzky-Golay Smoothing Applied to Rapid Analysis of Soil Cr Content

- URL: https://www.scirp.org/journal/doi.aspx?doi=10.4236/gep.2021.93006
- Accessed: 2026-04-02
- Relevance: Savitzky-Golay 前処理のパラメータ探索

What seems useful here:

- SG 系は窓幅や次数の選び方で性能が動く
- 今回も `window=11`, `polyorder=2`, `deriv=1` 固定のままではなく、局所探索の価値がある

## Interpretation For This Project

- 精度改善のボトルネックは、モデル本体より波長選択の質である可能性が高い
- 次の一手は `VIP`, `CARS`, `iPLS`, `区間選択` のいずれか
- SG 微分は使うとしても、パラメータ固定で決め打ちしないほうがよい

## Candidate Experiments

- `VIP選択 + PLS`
- `区間選択 PLS`
- `SG window/polyorder/deriv` の小規模 sweep
