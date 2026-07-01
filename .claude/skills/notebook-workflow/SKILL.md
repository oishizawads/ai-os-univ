---
name: notebook-workflow
description: Notebook の既定運用。クリーンカーネルで上から再実行できる状態を保ち、再利用ロジックは src/ に抽出、papermill で自動実行に備える。
---

# Notebook Workflow

## Mission
Notebook を「再現できる探索の場」に保つ。隠れ状態に依存した動かないノートを残さない。

## Rules
- **クリーンカーネルで上から順に再実行できる**状態を保つ（出力をクリアして Run All が通る）。実行順依存の隠れ状態を作らない。
- セルで育った**再利用ロジックは `src/` に関数として抽出**し、Notebook からは import して使う（[[python-style]] に従う）。
- パラメータはセル先頭にまとめる。自動実行する場合は **papermill** のパラメータセル（`# parameters` タグ）にする。
- 入出力パスは [[path-io]]、データ層の扱いは [[safe-data-handling]] に従う。
- **ローカルGPUが無くリモート（Colab/Kaggle）で回す場合**は Notebook を `!python run.py` を叩くだけの thin switch にする → [[remote_gpu_runner_kaggle]]。
- 大きな出力やデータをノートに焼き込んでコミットしない。重い出力はクリアするか別ファイルへ。

## Workflow
1. 探索は Notebook で素早く回す。
2. 固まった処理は関数化して `src/` へ移し、Notebook 側は呼び出すだけにする。
3. 提出/共有前に「Restart & Run All」で通ることを確認する。
4. 定期実行・バッチ化が要るなら papermill でパラメータ実行に載せる。

## Guardrails
- 実行順に依存して「いまだけ動く」ノートを共有しない。
- 同じ前処理を複数ノートにコピペで増殖させない。`src/` に寄せる。
- 巨大な出力セルや実データを焼き込んだままコミットしない。
