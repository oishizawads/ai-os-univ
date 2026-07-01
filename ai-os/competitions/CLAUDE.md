# Competitions - CLAUDE.md

## Overview
MLコンペの管理ディレクトリ。

## Active
- `near-infrared-challenge/` ← 木材NIRスペクトル→含水率予測
- `atmaCup11/` ← 美術品画像→製作年代予測（RMSE）。独立gitリポジトリ
- `ml-selection-assignment/` ← MLエンジニア選考課題シリーズ（`README.pdf`=仕様 / `01-nfl-draft-prediction` / `02-superstore-marketing`）

## ディレクトリ規約
- 1コンペ=1ディレクトリ。zip等の生DLは展開後に残さない（展開dirが正典）
- ディレクトリ名は意味のあるスラッグにする（Google Drive由来の機械名は使わない）
- `competitions/` は workspace の **gitignore対象**（履歴なし）。削除は不可逆＝消す前に確認

## 共通原則
- CVが不安定な案は本命にしない
- train/test樹種非重複など **data leakage** を最重視
- LOSO CV を主軸。ランダムCVは参考値のみ
- 前処理・validationを先に詰める。いきなり深層に飛ばない
- 物理的根拠（水吸収帯など）のある前処理を優先

## Workflow
1. `<comp>/SESSION_NOTES.md` → `COMPETITION.md` → `VALIDATION_RULES.md` の順に読む
2. 実験前に `.steering/` を切る（requirements, design, tasklist）
3. 重い処理（LOSOループ、GridSearch）は **Codex** に投げる
4. 実験後に `SESSION_NOTES.md` + `experiment_ledger.csv` を更新

## よく使うAgent（コンペ）
- `kaggle-researcher` — Kaggle特化の調査（過去解法・前処理・validation論点・solid/explosive戦略）
- `researcher` — 論文・手法・技術選定の横断調査（コンペ・実務共通）
- `data-analyst` — EDA・失敗分析
- `experiment-planner` — 次の実験の設計と優先順位
- `code-reviewer` — 実装レビュー（leakチェック含む）
- `error-analyzer` — 異常スコア・学習崩れの診断
