# Experiment Ledger Template

このテンプレートは、コンペでも実務でも使える「総当たり実験台帳」の雛形です。

## Files

- `experiment_ledger_template.csv`: 実験一覧
- `src/ledger_runner.py`: CSV を順次実行して結果を記録する汎用ランナー

## Required Columns

- `experiment_id`: 一意な ID
- `priority`: 実行優先度。小さいほど先
- `enabled`: 実行対象かどうか
- `status`: `planned`, `ready`, `running`, `completed`, `failed`, `spec_only`
- `theme`: 人間向けの短い説明
- `family`: 前処理、波長選択、モデル、アンサンブルなどの分類
- `preprocessing`: 手法名
- `selector`: 波長選択名
- `model`: モデル名
- `validation`: 検証方式
- `command`: 実際に実行するコマンド
- `workdir`: 実行ディレクトリ
- `submission_expected`: submission を作る想定か
- `source_note`: 論文・コンペ・業務知見の由来
- `notes`: 自由メモ

## Recommended Workflow

1. 論文や過去案件から候補を並べる
2. `status=spec_only` で仕様だけ先に置く
3. 実装したら `command` を埋めて `status=ready` にする
4. `src/ledger_runner.py` で順次実行する
5. `summary.csv` と `result.md` を確認して次の枝を決める
