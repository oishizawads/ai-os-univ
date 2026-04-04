# Literature Ledger Design

## Goal

論文知ベースの実験候補を、比較可能で再開可能な台帳として管理する。

## Constraints

- 既存の `experiments/` 構造を崩さない
- 実験コード本体は必要になったときに追加する
- 先に「何をやるか」を 30 本前後の ledger として確定する
- 他コンペ・実務にも流用できる形にする

## Chosen Approach

- 汎用テンプレートは `research/templates/` に置く
- 汎用ランナーは `src/ledger_runner.py` に置く
- このコンペ固有の 30 本台帳は `.steering/2026-04-02-literature-ledger/experiment_ledger.csv` に置く
- 実装済み実験だけ `command` を埋めて順次実行する

## Why This Fits

- 既存の `experiments/expAxxx_*` を壊さない
- 研究知見と実験管理を分離できる
- 将来の別案件でも CSV を差し替えるだけで流用できる
