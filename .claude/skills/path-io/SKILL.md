---
name: path-io
description: パスとI/Oの既定ルール。pathlib.Path を使い、ハードコード絶対パス禁止、出力時は親ディレクトリを自動作成。
---

# Path and I/O

## Mission
環境に依存しない、壊れない入出力を書く。ファイルパスを扱う全タスクで適用する。

## Rules
- パスは `pathlib.Path` で扱う。文字列連結や `os.path.join` の手組みを避ける。
- ハードコードした絶対パス（`C:\Users\...` や `/home/...`）を書かない。プロジェクトルートや設定からの相対で解決する。
- 出力前に親ディレクトリを作る：`path.parent.mkdir(parents=True, exist_ok=True)`。
- 入出力のパスは関数引数・設定・定数にまとめ、処理の奥に埋め込まない。
- 読み込みは存在確認、書き込みは上書き可否を意識する（raw層は [[safe-data-handling]] に従い不変）。

## Recommended pattern
```python
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
out_path = PROJECT_ROOT / "data" / "processed" / "result.parquet"
out_path.parent.mkdir(parents=True, exist_ok=True)
df.write_parquet(out_path)
```

## Guardrails
- 絶対パスをコードに直書きしない（再現性と共有性が壊れる）。
- 親ディレクトリ未作成の `FileNotFoundError` を出さない。先に mkdir。
- パスを `str` のまま引き回さない。`Path` を境界で受ける。
