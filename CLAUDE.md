ｚ# Workspace - CLAUDE.md

## Overview
全作業は `ai-os/` 配下で管理する。

```
ai-os/
  competitions/          ← MLコンペ（Kaggle等）
  work/
    company/             ← 社内OS・提案・PoC
    clients/             ← クライアント案件
    internal/            ← 社内ツール・再利用モジュール
  knowledge-pipeline/    ← Web記事の収集・検索・wiki化
  obsidian-vault/        ← 外部情報の蓄積（raw記事・wiki）
  knowledge/             ← 構造化知識資産（principles/playbooks等）
  decisions/             ← 横断的意思決定ログ（月別 YYYY-MM.md）
  shared/                ← 共通プロンプト・標準・スニペット
  templates/             ← プロジェクトテンプレート
```

## Role
- **Claude** = PM（設計・判断・レビュー）
- **Codex** = Engineer（実装・実験・重い処理）

Codexへの投入（スキル経由）:
```
/codex:rescue タスク記述...
```

Codexへの投入（直接実行）:
```bash
node "$HOME/.claude/plugins/marketplaces/openai-codex/plugins/codex/scripts/codex-companion.mjs" task "..." --write
```

## Session開始
```bash
python C:/workspace/ai-os/hooks/lib/session_start.py [project_dir]
```
SESSION_NOTES.md / .steering/ / experiment_ledger.csv / DECISION_LOG.md を自動表示する。

---

## Agent Catalog

### 分析・調査

| Agent | 使うとき |
|-------|---------|
| `data-analyst` | EDA、分布確認、失敗分析、仮説整理 |
| `researcher` | 手法調査、論文調査、先行事例、技術選定候補 |
| `web-summarizer` | 記事・ドキュメントの要点まとめ |

### 設計・計画

| Agent | 使うとき |
|-------|---------|
| `experiment-planner` | 実験・PoCの設計、優先順位づけ、次手の決定 |
| `product-analyst` | 業務要件整理、KPI、利害関係者、価値検証 |

### レビュー・診断

| Agent | 使うとき |
|-------|---------|
| `code-reviewer` | MLコード・プロダクションコードのレビュー |
| `backend-reviewer` | API・バッチ・インフラ・設定のレビュー |
| `error-analyzer` | エラー・異常スコア・壊れた学習の原因特定 |

---

## Context切り替え
- コンペ作業: `ai-os/competitions/<name>/` に入る → `CLAUDE.md` が自動で読まれる
- 実務: `ai-os/work/company/` → `CLAUDE.md` 参照
- 客先案件: `ai-os/work/clients/<name>/` → 案件固有の指示があればそちらを優先
- 知識ベース: `ai-os/knowledge-pipeline/` で管理（`--ingest` → `--embed-only` → `--query`）

## Session開始時
1. 該当ディレクトリの `CLAUDE.md` を読む
2. `SESSION_NOTES.md` を読む
3. 必要なら `experiment_ledger.csv` or 最新実験メモを確認
