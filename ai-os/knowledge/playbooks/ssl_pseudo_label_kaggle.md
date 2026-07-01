---
title: "SSL 事前学習と擬似ラベル（リーク境界に注意）"
type: playbook
domain: ml
tags: [kaggle, ssl, self-supervised, pseudo-label, pretraining, domain-adaptation, leakage]
created: 2026-06-05
source:
  title: "LAIME Kaggle Dojo ミーティング知見（SSL/擬似ラベル）"
  author: "LAIME メンバー（岡村）＋メンター"
  isbn: ""
  chapter: ""
---

## Summary
精度を伸ばす中〜上級テクとして、SSL（自己教師あり）事前学習と擬似ラベル（pseudo label）。
**重要なリーク境界**：testデータを**画像としてのみ（正解ラベルを使わず）**事前学習に使うのはリークではなく、SSLではむしろ推奨。本番データで事前学習すると**ドメイン適応**の効果もある。

## Core Principles
- **「ラベルを使うか」がリークの境界**。test画像をラベルなしで表現学習に使うのはOK。test正解を学習に混ぜるのはNG。
- **本番データでpretrain = ドメイン適応**。train と本番の分布が違うとき、本番データでの事前学習がギャップを埋める。
- **擬似ラベルは反復で伸びる**。予測→高確信サンプルにラベル付け→再学習（2nd generation…）。

## Decision Rules
- **SSL事前学習を使う**：ラベル付きデータが少ない／train と test の分布差が大きいとき。test を含む手元の画像全部を**ラベルなしで**表現学習に回す。
- **擬似ラベルを使う**：未ラベル（or test）データが多く、ベースが安定しているとき。確信度の高い予測だけをラベル化。世代を重ねて改善を見る。
- **コンペルール確認**：test利用や外部データの可否はコンペ規約に従う（[[timm_usage]] の pretrained 可否と同じく要確認）。

## Procedure（擬似ラベル）
1. ベースモデルで未ラベル/testを予測。
2. 確信度の高いサンプルだけ擬似ラベルを付与。
3. 元の学習データ＋擬似ラベルで再学習。
4. CVで効果を確認し、改善するなら次世代へ（2nd generation）。

## Anti-patterns
- **testの「正解ラベル」を学習に使う** → 明確なリーク。使ってよいのは画像（入力）だけ。
- **低確信の擬似ラベルを大量投入** → ノイズで悪化。確信度で絞る。
- **擬似ラベルの効果をLBだけで判断** → CVで見る（[[kaggle_experiment_strategy]]）。
- **世代をまたぐリーク（Gen2リーク）** → Gen2 で validation として扱うデータを、Gen1 の学習データに使っていると**リークになる**。世代間でデータの役割が混ざらないよう管理する。擬似ラベルは「注意しないとすぐリークする」前提で扱う。

## Example
画像コンペ：train少 → 手元全画像（test含む、ラベルなし）でSSL pretrain → 下流をfine-tune。さらにtestへ擬似ラベルを付け、確信度上位だけで再学習し世代更新。

## Eval
- 事前学習でtestの「ラベル」を使っていない（画像のみ）。
- 擬似ラベルを確信度で絞り、CVで効果検証している。
- test/外部データ利用がコンペルールに沿っている。

## 関連
- [[kaggle_experiment_strategy]] — CVで効果を見る
- [[image_baseline_tuning_kaggle]] / [[timm_usage]] — 事前学習・モデルの土台
