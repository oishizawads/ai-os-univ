---
name: python-ops
description: Python プロジェクト運用の既定。新規個人プロジェクトは uv 推奨、Kaggle/納品は pip/conda 許容。品質は ruff→pytest→mypy の順。
---

# Python Project Operations

## Mission
環境構築・依存管理・品質チェックの入口を揃える。パッケージ管理は**推奨**であって強制ではない。

## パッケージ管理（ハイブリッド方針）
- **uv を推奨**: 自分の新規個人プロジェクト。速くて lockfile が固い。
  - `uv sync`（依存導入）/ `uv add <pkg>` / `uv run <cmd>`。
- **pip / conda を許容**: 以下では無理に uv へ寄せない。
  - Kaggle 環境・Colab・既存の conda 前提プロジェクト
  - クライアントが特定のツールチェーンを指定している
- どれを使うにせよ、**依存は lock/requirements で固定**し再現可能にする。

## 品質チェックの順序
新規・変更コードには次の順で回す（ローカルは `python scripts/run_quality_checks.py`）:
1. `ruff check`（lint）
2. `ruff format --check`（整形差分）
3. `mypy`（型）
4. `pytest`（テスト）

CI でも同じ並び（`.github/workflows/ai-verify.yml`）。コミット前ガードは [[safe-data-handling]] を pre-commit で強制。

## Guardrails
- 「uv じゃないとダメ」で Kaggle/納品環境を壊さない。推奨は推奨。
- 依存を固定せず「手元で動いた」で済ませない。
- 品質チェックを飛ばして緑のふりをしない。失敗は失敗として報告する。
- コードスタイルは [[python-style]] に従う。
