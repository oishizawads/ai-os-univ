# Spectral Regression Competitions

## Scope

NIR/MIR/スペクトル回帰の過去コンペや、その周辺の競技知見を蓄積する。

## Items

### 1. SS4GG Hackathon: NIR Spectroscopy Modelling

- URL: https://www.kaggle.com/competitions/ss4gg-hackathon-nir-neospectra/overview
- Accessed: 2026-04-02
- Relevance: NIR スペクトル回帰コンペとして近い

What seems useful here:

- 高次元スペクトル回帰では、前処理と validation の設計が順位に直結しやすい
- モデルを複雑化するより、妥当な baseline と feature engineering が重要

### 2. Mid infrared spectroscopy and milk quality traits: a data analysis competition

- URL: https://www.sciencedirect.com/science/article/pii/S0169743921002100
- Accessed: 2026-04-02
- Relevance: スペクトル回帰コンペを論文としてまとめたもの

What seems useful here:

- タスクごとに効くモデルは異なるが、前処理と validation の影響が大きい
- 単一モデルに固執せず、複数の線形系モデルを比べるのが自然

### 3. What is to be gained by ensemble models in analysis of spectroscopic data?

- URL: https://www.sciencedirect.com/science/article/pii/S0169743923001867
- Accessed: 2026-04-02
- Relevance: スペクトルデータにおけるアンサンブルの価値

What seems useful here:

- スペクトル回帰ではアンサンブルが単独モデルより安定することがある
- 今回も `PLS`, `Ridge`, 前処理違いの submission 平均を試す根拠になる

## Interpretation For This Project

- validation を甘くすると本番で崩れやすい
- baseline の堅さが重要
- 最後はアンサンブルで伸ばすのが王道

## Candidate Experiments

- `expA004`, `expA005`, `expA008` の平均提出
- 同一モデルの前処理違いブレンド
