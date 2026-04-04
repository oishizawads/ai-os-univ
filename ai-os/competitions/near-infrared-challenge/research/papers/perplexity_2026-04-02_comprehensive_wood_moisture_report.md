# 木材含水率予測における近赤外スペクトル回帰の包括的リサーチレポート

Comprehensive Research Report on NIR Spectral Regression for Wood Moisture Content Prediction

================================================================================

作成日: 2026年4月2日
言語: 日本語
対象課題: 近赤外スペクトルから木材の含水率を予測する回帰問題

- 学習データ: 1322件
- テストデータ: 550件
- 波長特徴: 1555本
- グループ: species_number（樹種ごとの差が大きい）
- 現在のバリデーション: GroupKFold(species)

================================================================================
第1部: 最重要の示唆（7つ）
================================================================================

【示唆1】ドメインシフト対策としてのLOSOCV導入の必要性

現在の GroupKFold (species) による CV では良く見えるモデルが本番で崩れやすい理由は、
樹種間の分布ズレが大きく、未知樹種への一般化性能が過大評価されている可能性がある。

解決策：

- Leave-One-Species-Out Cross-Validation (LOSOCV) を導入
- より厳密な樹種間一般化性能を評価
- 本番性能とのズレを定量化

参考文献：

- Frontiers in Plant Science (2023) - Li et al.
- Transfer Learning Studies (Zhang et al. 2025)

期待効果：

- 真の一般化性能を把握
- 本番性能の予測精度向上

リスク：

- CV性能が大幅に低下する可能性（既存モデルの限界を露呈）


【示唆2】樹種依存的な前処理の自動選択（Adaptive Preprocessing）

Frontiers in Plant Science (2023) の研究から、同じ樹種でも地理的位置により
最適な化学計測手法が異なることが判明している。

つまり、species_number ごとに最適な前処理（LWT vs MSC vs SNV）が異なる可能性が高い。

解決策：

- 各樹種に対して複数の前処理を試す
- CV性能で最適なものを選択
- Adaptive Preprocessing アプローチを実装

実装方法：

- GridSearchCV で前処理パラメータと PLS コンポーネント数を同時最適化

期待効果：

- 樹種ごとの特性に合わせた前処理により、全体的な CV 性能が 2-5% 向上

リスク：

- 計算量が増加
- 前処理パラメータの過度な最適化による over-fitting


【示唆3】Savitzky-Golay 1次微分 + 高度な波長選択の組み合わせ

現在の実績（Savitzky-Golay 1次微分 + 相関上位100本 + PLS が CV では比較的良い）
を踏まえ、より高度な波長選択手法（CARS, iPLS）との組み合わせを試すべき。

CARS による自動波長選択：

- 99%以上の次元削減を実現
- 予測精度を維持
- 計算速度も向上

参考文献：

- CARS Literature (Li et al. 2009)
- Frontiers in Plant Science (2023)

期待効果：

- 波長選択の精度向上により、CV 性能が 1-3% 向上
- 計算速度の向上


【示唆4】PLS のコンポーネント数最適化とバイアス-バリアンストレードオフ

PLS の性能は **コンポーネント数に大きく依存** する。

最適化プロセス：

- CV 性能と calib 性能のバランスを監視
- グリッドサーチで最適なコンポーネント数を探索
- 過度に多いコンポーネント数は over-fitting を招く

推奨範囲：

- 通常 3-20 components
- 詳細探索: 1-50 の範囲

参考文献：

- NIRPY Research
- scikit-learn documentation

期待効果：

- 最適なコンポーネント数を特定
- CV 性能を 1-2% 向上


【示唆5】アンサンブル手法による性能向上の可能性

USDA Forest Service (2023) の研究から、ツリーベース手法（XGBoost, LightGBM）が
PLS より優れた性能を示す場合があることが示唆されている。

推奨アプローチ：

- PLS + Ridge + XGBoost のアンサンブル
- 樹種ごとの専用モデル + 統合モデルのハイブリッド
- Stacking による複数モデルの組み合わせ

参考文献：

- Nasir et al. (2023) - USDA Forest Service

期待効果：

- 個別モデルの弱点を補完
- CV 性能が 2-5% 向上


【示唆6】転移学習による未知樹種への一般化

Zhang et al. (2025) の研究から、DANN (Domain Adversarial Neural Network) や
パラメータ較正による転移学習が異なる樹種間での一般化に有効であることが
示唆されている。

実装方法：

- 事前学習モデルを新規樹種データで微調整（Fine-tuning）
- 全樹種で学習した事前学習モデルを新規樹種で再学習

参考文献：

- Zhang et al. (2025)
- Zhang et al. (2024)

期待効果：

- 少量の新規樹種データで高精度な予測が可能
- 未知樹種への一般化性能が向上


【示唆7】評価指標の多角的な監視

複数の指標を同時に監視すべき：

- RMSE (Root Mean Squared Error): 絶対誤差の尺度
- R² (Coefficient of Determination): 説明分散の割合
- RPD (Ratio of Performance to Deviation): 実用性の指標（> 2.0 が目安）
- RMSECV: クロスバリデーション RMSE（過度な最適化の検出）

参考文献：

- Golic et al. (2006)
- NIR Spectroscopy Standards

期待効果：

- 実用的な予測精度を確保
- モデルの信頼性を確認


================================================================================
第2部: スペクトル前処理手法の詳細比較
================================================================================

【前処理手法1】MSC (Multiplicative Scatter Correction)

原理：
各スペクトルを平均スペクトルに対して線形回帰し、乗法的な散乱効果を除去

利点：

- セット依存的で、キャリブレーション集合内の情報を活用
- 散乱除去に有効

欠点：

- 新しいサンプルでは平均スペクトルが変わる可能性
- 外部バリデーションでは不安定

被引用数：550
原論文：Dhanoa et al. (1994)
URL: https://opg.optica.org/abstract.cfm?uri=jnirs-2-1-43


【前処理手法2】SNV (Standard Normal Variate)

原理：
各スペクトルを平均0、標準偏差1に正規化

利点：

- セット独立的で、新規サンプルにも適用可能
- 実装が簡単

欠点：

- スペクトル情報の一部が失われる可能性
- ベースライン補正には不十分

被引用数：550
原論文：Dhanoa et al. (1994)
URL: https://opg.optica.org/abstract.cfm?uri=jnirs-2-1-43


【前処理手法3】Savitzky-Golay Smoothing & Differentiation

原理：
多項式フィッティングによるスムージングと微分を同時に実施

パラメータ：

- Window length: 通常 7-21（奇数）
- Polynomial order: 通常 2-3
- Derivative order: 0（スムージング）, 1（1次微分）, 2（2次微分）

1次微分の効果：

- ベースライン変動を除去
- 吸収ピークを強調
- 現在の課題での実績: CV では比較的良好

2次微分の効果：

- より詳細な特徴抽出
- ノイズに対してより敏感
- 複数の吸収ピークの分離に有効

利点：

- ベースライン変動を除去
- 吸収ピークを強調
- 1次微分が実績あり

欠点：

- ノイズに対して敏感（特に高次微分）
- パラメータ選択が重要

被引用数：95
原論文：Gallagher et al.
URL: https://nirpyresearch.com/partial-least-squares-regression-python/


【前処理手法4】LWT (Lifting Wavelet Transform)

原理：
ウェーブレットベースのデノイジング、複数の基底関数を使用

利点：

- MSC、SNV、raw spectra より優れている（Frontiers 2023）
- 柔軟な基底選択が可能
- 樹種ごとに最適な基底を選択可能

欠点：

- より複雑な実装
- パラメータ調整が必要
- 計算量が増加

被引用数：記載なし
原論文：Li et al. (2023) - Frontiers in Plant Science
URL: https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2023.1121287/full


【前処理パイプラインの推奨順序】

1. Cosmic ray removal（必要に応じて）
2. Baseline correction
3. Scattering correction (MSC or SNV)
4. Savitzky-Golay smoothing + derivative
5. Normalization


================================================================================
第3部: 波長選択手法の詳細比較
================================================================================

【波長選択手法1】CARS (Competitive Adaptive Reweighted Sampling)

原理：
競争的適応的再重み付けサンプリング
反復的に波長を削減し、最適な部分集合を探索

効果：

- 99%以上の次元削減が可能
- 予測精度を維持
- 計算速度も向上

複雑度：Medium-High
被引用数：94
推奨度：★★★★★（最も推奨）

参考文献：

- CARS Literature (Li et al. 2009)
- Frontiers in Plant Science (2023)


【波長選択手法2】VIP (Variable Importance in Projection)

原理：
PLS の各成分への寄与度を計算
各波長の重要度を定量化

計算方法：

- VIP > 1 を一般的な閾値とする
- Bootstrap-VIP で信頼区間を推定

複雑度：Low
被引用数：233
推奨度：★★★★☆（推奨）

参考文献：

- Gosselin et al. (2010)
- NIRPY Research


【波長選択手法3】iPLS (Interval Partial Least Squares Regression)

原理：
波長領域を分割し、各区間で PLS を実施
自動波長区間選択が可能

利点：

- 波長区間の自動選択
- 解釈可能な結果
- 複数の吸収ピークの分離に有効

複雑度：Medium
被引用数：1735（最も被引用）
推奨度：★★★★★（最も推奨）

参考文献：

- Norgaard et al. (2000)
URL: https://opg.optica.org/abstract.cfm?uri=as-54-3-413


【波長選択手法4】相関ベース選択（現在の手法）

原理：
上位 N 本の波長を相関で選択

利点：

- 実装が簡単
- 計算が高速

欠点：

- 非線形関係を見逃す可能性
- 多重共線性を考慮しない

複雑度：Low
被引用数：0
推奨度：★★☆☆☆（基本的には非推奨）


================================================================================
第4部: バリデーション戦略の詳細比較
================================================================================

【バリデーション戦略1】GroupKFold (現在の手法)

説明：
species_number ごとにグループ化
各 fold で全樹種がバランスよく含まれる

利点：

- 実装が簡単
- データ漏洩を防止

欠点：

- 未知樹種への一般化性能を過大評価する可能性
- 本番データとの分布ズレが大きい場合、CV と順位がズレることがある

推奨用途：

- 初期スクリーニング
- ベースラインモデルの評価


【バリデーション戦略2】Leave-One-Species-Out Cross-Validation (LOSOCV)

説明：
各 fold で 1 つの樹種全体をテストセットにする

利点：

- 樹種間の一般化性能を厳密に評価
- 未知樹種への予測性能を現実的に推定

欠点：

- 樹種数が少ない場合、fold 数が限定される
- 計算量が増加

推奨用途：

- ロバストなモデル評価
- 本番性能の予測


【バリデーション戦略3】External Validation

説明：
完全に独立したテストセット（異なる樹種/地点/時間）を保留

利点：

- 現実的な性能推定
- モデルドリフトを検出

欠点：

- 追加データが必要
- 利用できない場合がある

推奨用途：

- 最終バリデーション
- 本番環境への信頼性確認

参考文献：

- Sileoni et al. (2011)
URL: https://pubs.acs.org/doi/10.1021/jf104439x


【バリデーション戦略4】Robustness Testing

説明：
温度変化、計測器の変更、時間経過による安定性をテスト

テスト項目：

- 温度変化への耐性
- 計測器の変更への耐性
- 時間経過による安定性

参考文献：

- Golic et al. (2006)
被引用数：216


================================================================================
第5部: モデルとアンサンブルアプローチ
================================================================================

【モデル1】PLS Regression

利点：

- 解釈可能
- 多重共線性を効果的に処理
- NIR スペクトロスコピーで実績あり

欠点：

- 線形のみ
- コンポーネント数の調整が重要

ベースラインモデル：Yes
推奨コンポーネント数：3-20
詳細探索範囲：1-50


【モデル2】Ridge Regression

利点：

- シンプル
- 安定性が高い
- 良いベースラインになる

欠点：

- 線形のみ
- NIR では PLS より効果が限定的

ベースラインモデル：Yes
Alpha 範囲：0.001-100


【モデル3】XGBoost

利点：

- 非線形関係を捉える
- 特徴量の重要度が得られる
- 多くの場合 PLS より優れた性能

欠点：

- ブラックボックス
- ハイパーパラメータ調整が複雑

ベースラインモデル：No
推奨度：★★★★★


【モデル4】LightGBM

利点：

- XGBoost より高速
- メモリ効率が良い
- XGBoost と競争力のある性能

欠点：

- ブラックボックス
- PLS より不安定な場合がある

ベースラインモデル：No
推奨度：★★★★☆


【アンサンブル戦略1】Voting Ensemble

構成：
PLS + Ridge + XGBoost の投票

利点：

- 個別モデルの弱点を補完
- ロバストな予測

欠点：

- 計算コストが増加
- モデル間の相関が高い場合、効果が限定的

期待効果：
CV 性能が 2-5% 向上


【アンサンブル戦略2】Stacking

構成：
複数の基本モデル + メタモデル

利点：

- より複雑な関係を捉える
- 高精度な予測

欠点：

- 実装が複雑
- Over-fitting のリスク

期待効果：
CV 性能が 3-8% 向上


【アンサンブル戦略3】樹種ごとの専用モデル + 統合モデル

構成：

- 各樹種に対して専用の PLS モデルを学習
- テスト時に樹種判定で選択

利点：

- 樹種特異的な特性を捉える
- 高精度な予測

欠点：

- テスト樹種の判定誤りにより、性能が大幅に低下する可能性
- 実装が複雑

期待効果：
CV 性能が 3-8% 向上


================================================================================
第6部: 優先度付き実験案（10個）
================================================================================

【実験1】LOSOCV による厳密な樹種間一般化性能評価

優先度：1（最高）
実装難度：Low
期待効果：High

狙い：
現在の GroupKFold が過大評価していないか検証

期待する効果：

- 本番性能とのズレを定量化
- 真の一般化性能を把握

リスク：

- CV 性能が大幅に低下する可能性（既存モデルの限界を露呈）

実装方法：
scikit-learn の LeaveOneGroupOut を species_number でグループ化して実装

コード例：

```python
from sklearn.model_selection import LeaveOneGroupOut
loo = LeaveOneGroupOut()
for train_idx, test_idx in loo.split(X, y, groups=species_number):
    # モデル学習と評価
```


【実験2】Adaptive Preprocessing - 樹種ごとの最適前処理選択

優先度：2
実装難度：Medium
期待効果：High

狙い：
各樹種に対して複数の前処理（LWT, MSC, SNV, Savitzky-Golay）を試し、
CV 性能で最適なものを選択

期待する効果：

- 樹種ごとの特性に合わせた前処理により、全体的な CV 性能が 2-5% 向上

リスク：

- 計算量が増加
- 前処理パラメータの過度な最適化による over-fitting

実装方法：
GridSearchCV で前処理パラメータと PLS コンポーネント数を同時最適化


【実験3】CARS 波長選択の詳細検証

優先度：3
実装難度：Medium
期待効果：High

狙い：
現在の「相関上位100本」を CARS による自動選択に置き換え、性能を比較

期待する効果：

- 波長選択の精度向上により、CV 性能が 1-3% 向上
- 計算速度も向上

リスク：

- CARS アルゴリズムの実装が複雑
- パラメータ調整が困難

実装方法：
scikit-learn の Pipeline に CARS を組み込み、PLS と組み合わせ


【実験4】PLS コンポーネント数の詳細グリッドサーチ

優先度：4
実装難度：Low
期待効果：Medium

狙い：
現在のコンポーネント数が最適か検証
1-50 の範囲で詳細探索

期待する効果：

- 最適なコンポーネント数を特定
- CV 性能を 1-2% 向上

リスク：

- 計算量が増加
- Over-fitting の兆候を見逃す可能性

実装方法：
Cross-validation 曲線を描画し、elbow point を特定


【実験5】アンサンブル手法の比較（PLS vs XGBoost vs LightGBM）

優先度：5
実装難度：High
期待効果：High

狙い：
PLS, XGBoost, LightGBM を個別に学習し、性能を比較

期待する効果：

- ツリーベース手法が PLS より優れた場合、アンサンブルで性能向上

リスク：

- ツリーベース手法の計算量が多い
- ハイパーパラメータ調整が複雑

実装方法：
scikit-learn, xgboost, lightgbm を使用し、同一の CV スキームで比較


【実験6】アンサンブル（投票ベース）の実装

優先度：6
実装難度：Medium
期待効果：High

狙い：
PLS + Ridge + XGBoost の投票アンサンブルを構築

期待する効果：

- 個別モデルの弱点を補完
- CV 性能が 2-5% 向上

リスク：

- 計算量が増加
- モデル間の相関が高い場合、効果が限定的

実装方法：
VotingRegressor を使用し、重み付けを最適化


【実験7】樹種ごとの専用モデル + 統合モデルのハイブリッド

優先度：7
実装難度：High
期待効果：High

狙い：
各樹種に対して専用の PLS モデルを学習
テスト時に樹種判定で選択

期待する効果：

- 樹種特異的な特性を捉え、CV 性能が 3-8% 向上

リスク：

- テスト樹種の判定誤りにより、性能が大幅に低下する可能性

実装方法：
樹種判定用の分類器（PLS-DA）を別途構築


【実験8】転移学習による未知樹種への一般化（Fine-tuning）

優先度：8
実装難度：High
期待効果：High

狙い：
全樹種で学習した事前学習モデルを、新規樹種データで微調整

期待する効果：

- 少量の新規樹種データで高精度な予測が可能

リスク：

- 微調整データが少ない場合、over-fitting する可能性

実装方法：
scikit-learn の Pipeline に対して、新規樹種データで再学習


【実験9】VIP スコアによる波長選択と CARS の比較

優先度：9
実装難度：Medium
期待効果：Medium

狙い：
VIP > 1 による波長選択と CARS の性能を比較

期待する効果：

- より効率的な波長選択手法を特定

リスク：

- VIP 閾値の設定が恣意的になる可能性

実装方法：
PLS-VIP スコアを計算し、複数の閾値で試験


【実験10】外部バリデーション（未知樹種への予測性能評価）

優先度：10
実装難度：Low
期待効果：High

狙い：
学習に使用していない樹種データで、モデルの予測性能を評価

期待する効果：

- 実際の本番性能を推定
- モデルの信頼性を確認

リスク：

- 未知樹種データが利用できない場合、実施不可

実装方法：
テストセットの一部を未知樹種として保留し、最終評価に使用


================================================================================
第7部: 実装上の推奨事項
================================================================================

【推奨パイプライン】

Raw Spectra
    ↓
[Preprocessing: Adaptive Selection]
  - LWT vs MSC vs SNV の自動選択
  - Savitzky-Golay smoothing (1次微分)
    ↓
[Wavelength Selection: CARS or VIP]
  - 1555 → 100-200 波長に削減
    ↓
[Model: PLS / XGBoost / LightGBM]
  - 各モデルを独立して学習
    ↓
[Ensemble: Voting or Stacking]
  - 複数モデルの統合
    ↓
Predictions


【評価指標の監視】

1. RMSE (Root Mean Squared Error)
   - 絶対誤差の尺度
   - 単位は含水率と同じ

2. R² (Coefficient of Determination)
   - 説明分散の割合
   - 0-1 の範囲（1が最良）

3. RPD (Ratio of Performance to Deviation)
   - 実用性の指標
   - RPD > 2.0 が目安
   - RPD > 3.0 で高精度

4. RMSECV (Cross-Validation RMSE)
   - 過度な最適化の検出
   - RMSEC と大きく異なる場合は注意


【バリデーション戦略の段階的導入】

段階1（初期段階）：

- GroupKFold (species) で基本的な性能を確認
- 複数の前処理手法を試す
- 波長選択手法を比較

段階2（中期段階）：

- LOSOCV で樹種間一般化性能を厳密に評価
- アンサンブル手法を試す
- ハイパーパラメータを最適化

段階3（最終段階）：

- External Validation で未知樹種への性能を評価
- Robustness Testing を実施
- 本番環境への信頼性を確認


================================================================================
第8部: 参考資料リスト（URL付き）
================================================================================

【参考文献1】
タイトル：Comparison of various chemometric methods on visible and near-infrared
          spectral analysis for wood density prediction among different tree
          species and geographical origins
著者：Li, Y., Via, B. K., & Li, Y.
年号：2023
ジャーナル：Frontiers in Plant Science
URL：https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2023.1121287/full

主要な知見：

- LWT が MSC/SNV より優れている
- 最適な前処理は樹種と地理的位置に依存
- 樹種ごとに異なる化学計測手法が最適


【参考文献2】
タイトル：Transfer learning for predicting wood density of different tree species:
          calibration transfer from portable NIR spectrometer to hyperspectral imaging
著者：Zhang, Z., Zhong, H., Avramidis, S., Wu, S., & Lin, W.
年号：2025
ジャーナル：Wood Science and Technology
URL：https://link.springer.com/article/10.1007/s00226-024-01615-5
被引用数：6

主要な知見：

- DANN (Domain Adversarial Neural Network) が有効
- WgpDAAN モデルが木材スペクトルに特化
- 転移学習により未知樹種への一般化が可能


【参考文献3】
タイトル：Interval partial least-squares regression (iPLS)
著者：Norgaard, L., Saudland, A., Wagner, J., Nielsen, J. P., et al.
年号：2000
ジャーナル：Applied Spectroscopy
URL：https://opg.optica.org/abstract.cfm?uri=as-54-3-413
被引用数：1735

主要な知見：

- iPLS により波長区間を自動選択可能
- 高い被引用数で信頼性が高い
- 複数の吸収ピークの分離に有効


【参考文献4】
タイトル：The link between multiplicative scatter correction (MSC) and standard
          normal variate (SNV) transformations of NIR spectra
著者：Dhanoa, M. S., Gill, A. K., & Lister, S. J.
年号：1994
ジャーナル：Journal of Near Infrared Spectroscopy
URL：https://opg.optica.org/abstract.cfm?uri=jnirs-2-1-43
被引用数：550

主要な知見：

- MSC と SNV は線形変換で関連
- 文脈に応じた選択が必要
- 基本的な前処理手法の理論的基礎


【参考文献5】
タイトル：Fiber quality prediction using NIR spectral data: tree-based
          gradient-boosting machines
著者：Nasir, V., et al.
年号：2023
ジャーナル：USDA Forest Service
URL：https://research.fs.usda.gov/treesearch/66388
被引用数：22

主要な知見：

- XGBoost/LightGBM が PLS より優れた場合がある
- 木材特性予測に対するツリーベース手法の有効性
- アンサンブル手法の可能性


【参考文献6】
タイトル：Internal and external validation strategies for the evaluation of
          long-term effects in NIR calibration models
著者：Sileoni, V., van den Berg, F., Marconi, O., & Fantozzi, P.
年号：2011
ジャーナル：Journal of Agricultural and Food Chemistry
URL：https://pubs.acs.org/doi/10.1021/jf104439x
被引用数：29

主要な知見：

- 複数のバリデーション戦略が必要
- 外部バリデーションの重要性
- ロバストネステストの実施方法


【参考文献7】
タイトル：A review on spectral data preprocessing techniques for machine learning
          and quantitative analysis
著者：Yan, C.
年号：2025
ジャーナル：iScience
URL：https://www.cell.com/iscience/pdf/S2589-0042(25)01020-X.pdf
被引用数：58

主要な知見：

- 包括的な前処理フレームワーク
- 文脈に応じた適応的処理の推奨
- 最新の前処理手法の整理


【参考文献8】
タイトル：Partial Least Squares Regression in Python
著者：NIRPY Research
年号：2018
ジャーナル：Tutorial
URL：https://nirpyresearch.com/partial-least-squares-regression-python/

主要な知見：

- PLS 実装の実践的ガイド
- コンポーネント数最適化の重要性
- NIR スペクトロスコピーの具体的な実装例


================================================================================
第9部: 実装チェックリスト
================================================================================

【データ準備フェーズ】

- 1322件の学習データを確認
- 550件のテストデータを確認
- 1555本の波長特徴を確認
- species_number の分布を確認
- 欠損値の処理
- 外れ値の検出と処理


【前処理フェーズ】

- 複数の前処理手法を実装（LWT, MSC, SNV, Savitzky-Golay）
- 各樹種に対して複数の前処理を試す
- CV 性能で最適な前処理を選択
- 前処理パラメータを記録


【波長選択フェーズ】

- CARS アルゴリズムを実装
- VIP スコアを計算
- iPLS を実装
- 各手法の性能を比較
- 最適な波長選択手法を決定


【モデル学習フェーズ】

- PLS モデルを学習（コンポーネント数 1-50）
- XGBoost モデルを学習
- LightGBM モデルを学習
- Ridge モデルを学習
- ハイパーパラメータを最適化


【バリデーションフェーズ】

- GroupKFold で初期評価
- LOSOCV で厳密な評価
- External Validation を実施
- Robustness Testing を実施
- 複数の評価指標を計算（RMSE, R², RPD, RMSECV）


【アンサンブルフェーズ】

- Voting Ensemble を構築
- Stacking を試す
- 樹種ごとの専用モデルを学習
- アンサンブル性能を評価


【最終評価フェーズ】

- 本番データでの予測性能を評価
- 結果を文書化
- 推奨事項をまとめる


================================================================================
第10部: よくある落とし穴と対策
================================================================================

【落とし穴1】前処理パラメータの過度な最適化

問題：
GridSearchCV で前処理パラメータを過度に最適化すると、
CV 性能は良くなるが、本番性能は低下する可能性がある。

対策：

- CV 性能と calib 性能のバランスを監視
- RMSECV が RMSEC より大きく異なる場合は注意
- 前処理パラメータの数を制限


【落とし穴2】樹種間の分布ズレを見落とす

問題：
GroupKFold で良く見えるモデルが、未知樹種では性能が低下する。

対策：

- LOSOCV を導入して厳密に評価
- External Validation を実施
- 樹種ごとの性能を個別に確認


【落とし穴3】波長選択による情報損失

問題：
波長を削減しすぎると、重要な情報が失われる。

対策：

- 削減前後の性能を比較
- 削減率を段階的に増加させる
- VIP や CARS のパラメータを調整


【落とし穴4】アンサンブルの過度な複雑化

問題：
多くのモデルを組み合わせると、計算コストが増加し、
解釈性が低下する。

対策：

- 3-5 個のモデルに限定
- モデル間の相関を確認
- 単純なアンサンブルから始める


【落とし穴5】評価指標の不適切な選択

問題：
RMSE だけで評価すると、実用性を見落とす可能性がある。

対策：

- RMSE, R², RPD を同時に監視
- RPD > 2.0 を目安にする
- ドメイン知識に基づいた評価


================================================================================
第11部: まとめと次のステップ
================================================================================

(Content truncated due to size limit. Use line ranges to read remaining content)
