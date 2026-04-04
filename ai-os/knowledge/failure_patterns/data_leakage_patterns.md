---
title: "データリークの典型的パターン"
type: failure_pattern
domain: ds
tags: [leakage, target_leakage, preprocessing, feature_engineering]
created: 2026-04-05
---

## パターン1: Target Encodingのfold外計算

**何が起きたか**: カテゴリ変数のtarget encodingをfold分割前に計算した。CVスコアが異常に高く、テストで大幅に下落した。

**根本原因**: validation/testデータのターゲット情報がencoding値を通じてtrainに混入。

**検知方法**: target encodingしたカラムの特徴量重要度が異常に高い。ターゲットとの相関が0.9以上。

**対処**: `sklearn.model_selection.cross_val_predict` を使うか、Pipeline内でfold単位でfitする。

**再発防止**: 集計系の特徴量は全て「trainのみでfit」を確認するチェックリストに追加する。

---

## パターン2: Scalerをtestを含めてfit

**何が起きたか**: StandardScalerを`fit_transform(全データ)`した後にtrain/testに分けた。

**根本原因**: testの統計量（平均・分散）がscalingに使われ、testの情報がtrainの前処理に混入。

**検知方法**: trainとtestを分けた後でscalingすると数値が変わる。

**対処**: `scaler.fit(X_train)` → `scaler.transform(X_train)` / `scaler.transform(X_test)` の順序を守る。

**再発防止**: Pipelineを使う。`fit`は常にtrainのみ。コードレビューでfit対象を確認する。

---

## パターン3: 未来のlag特徴量

**何が起きたか**: 時系列予測で「予測時点tにおけるlag-1特徴量」を計算するとき、実際には時点t+1のデータを使っていた（インデックスのずれ）。

**根本原因**: `shift(1)` のタイミングと予測したい時刻のずれを正確に確認しなかった。

**検知方法**: lag特徴量がターゲットと異常に高い相関を持つ。予測が未来の実績値に近すぎる。

**対処**: 予測時点でどの情報が利用可能かを明示的に設計する。lag計算後に時系列順で確認する。

**再発防止**: 特徴量ごとに「予測時点tで実際に使えるデータか」をコメントで記載する。

---

## パターン4: testデータがtrainのグループに含まれる

**何が起きたか**: データを分割した後に気づいたが、testの一部サンプルと同一ユーザーのサンプルがtrainに存在していた。

**根本原因**: ランダム分割でグループ構造を無視した。

**検知方法**: ユーザーID等のグループ列でtrain/testの重複を確認する。

**対処**: GroupKFoldまたは明示的なグループ単位での分割に変更。重複グループをtrainから除外。

**再発防止**: データ分割直後にグループ列の重複チェックをルーティン化する。

---

## パターン5: data augmentation後の分割

**何が起きたか**: 画像・音声データをaugmentationした後にtrain/testに分割した。元サンプルとaugmentedサンプルが別のfoldに入った。

**根本原因**: augmentation後に分割すると、元サンプルの情報が異なるfoldに存在する状態になる。

**検知方法**: augmentationなしとCV差が小さすぎる（augmentation効果が見えない）。

**対処**: 元サンプルで分割してからaugmentationする。trainセットにのみaugmentationを適用する。

**再発防止**: augmentation → 分割 ではなく 分割 → augmentation の順序を徹底する。
