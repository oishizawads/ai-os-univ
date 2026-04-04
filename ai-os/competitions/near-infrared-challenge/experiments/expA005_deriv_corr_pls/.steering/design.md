# design.md — expA005_deriv_corr_pls

## 処理フロー

```
1. 全データに1次微分を適用（ターゲット非依存のため事前適用OK）
2. GroupKFold CV ループ:
   a. fold内train の |r(feature, target)| を計算
   b. 上位N件のインデックスを取得
   c. train/valid を選択済み特徴のみに絞って PLS 学習・評価
3. 最良 (n_top, n_components) を選択
4. 全trainで特徴選択 → 最終モデル学習 → payloadに保存
```

## ハイパーパラメータ候補
- N_TOP_FEATURES_CANDIDATES : [50, 100, 200, 400, 700]
- N_COMPONENTS_CANDIDATES   : [3, 5, 8, 10, 15, 20]
- n_components > n_top の組み合わせはスキップ

## リーク設計
| ステップ | リーク有無 | 理由 |
|---|---|---|
| 1次微分（全体適用） | なし | ターゲット非依存の変換 |
| 相関による特徴選択 | なし | fold内trainのみ使用 |
| 最終モデルの特徴選択 | 軽微 | 全trainでの計算（標準的実務慣行） |

## payloadに保存するもの
- model : 最終PLSモデル
- selected_feature_indices : 最終モデルで使った特徴インデックス
- best_n_top_features, best_n_components : 最良ハイパーパラメータ
- sweep_results : 全組み合わせのスコア
