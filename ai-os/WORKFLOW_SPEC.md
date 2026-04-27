# AI Workflow Operating System — 運用設計

Version 1.0 | 2026-04-05

---

## 1. この環境の構成

```
C:/workspace/
└── ai-os/                   ← 全作業の起点
    ├── competitions/         ← MLコンペ
    ├── work/                 ← 実務案件
    │   ├── company/
    │   ├── clients/
    │   └── internal/
    ├── knowledge-pipeline/   ← Web記事の収集・検索・wiki化
    ├── obsidian-vault/       ← 外部情報の蓄積（raw記事・wiki・reports）
    ├── knowledge/            ← 構造化知識資産
    ├── shared/               ← 共通リソース（使いながら蓄積）
    ├── templates/            ← プロジェクトテンプレート
    └── .claude/              ← AI実行設定（agents/commands/skills）
```

---

## 2. AI役割分担

| AI | 役割 | 使う場面 |
|----|------|---------|
| **Claude / Claude Code** | OS中核・文脈統合・設計・実装統括・知識運用 | 設計、要件定義、文書化、コード編集、Skills呼び出し |
| **GPT-5.4 Thinking** | 外部調査官 | 最新技術調査、論文横断、ベストプラクティス収集 |
| **Codex** | 長距離実装ワーカー | 長時間実装、反復コード修正、テストループ |

**原則**
- 調査を Claude に寄せすぎない（GPT-5.4 Thinkingを使う）
- 長時間実装を Claude に寄せすぎない（Codexを使う）
- 知識統合・最終判断は Claude 側に集約する

---

## 3. 知識の2層構造

この環境では知識を2種類に分けて管理する。

### Layer A: 外部収集情報 → `obsidian-vault/`
- Web Clipperでクリップした記事・論文
- `knowledge-pipeline` で管理（ingest → embed → query）
- LLMが書くwiki（`obsidian-vault/wiki/`）

### Layer B: 構造化知識資産 → `ai-os/knowledge/`
- 自分でキュレーションした原則・プレイブック
- フレームワーク・失敗パターン・評価項目
- **AIが直接参照する判断基準・手順**

---

## 4. ディレクトリ設計

```
ai-os/
├── CLAUDE.md               ← Claude向け運用ルール（既存）
├── WORKFLOW_SPEC.md        ← この文書
├── DECISION_LOG.md         ← 重要な意思決定の記録
├── EVAL_POLICY.md          ← 評価基準の定義
│
├── knowledge/              ← 構造化知識資産（AIが直接参照する判断基準）
│   ├── principles/         ← 長期不変の原則（イシュー思考・仮説思考・意思決定等）
│   ├── frameworks/         ← 思考フレームワーク（実験設計・モデル選択・評価設計等）
│   ├── playbooks/          ← 業務別標準手順（コンペ戦略・クライアント納品・PoC等）
│   └── failure_patterns/   ← 失敗パターンと教訓（CV設計・リーク・要件管理等）
│
├── .claude/                ← AI実行設定
│   ├── agents/             ← エージェント定義（data-analyst・code-reviewer等）
│   ├── commands/           ← コマンド定義（eda・baseline・submit等）
│   └── skills/             ← スキル定義（experiment-workflow・work-implementation等）
│
├── shared/                 ← 共通リソース（使いながら蓄積）
└── templates/              ← プロジェクトテンプレート（competition/client/steering）
```

---

## 5. 知識変換の標準フォーマット

raw情報（本・メモ・会議ログ）は以下の形式に変換してから保存する。

```markdown
---
title: ""
type: principle | playbook | framework | failure_pattern | eval_rule
domain: ds | ml | pm | rag | coding | general
tags: []
created: YYYY-MM-DD
source: ""
---

## Summary
（3〜5行で要点）

## Core Principles
- 原則1
- 原則2

## Decision Rules
- どう判断するか
- 適用条件
- 非適用条件

## Procedure
1. 手順1
2. 手順2

## Anti-patterns
- よくある失敗1
- よくある失敗2

## Eval
- この知識が正しく使われたかのチェック項目

## Tags
```

---

## 6. ワークフロー全体像

```
[外部情報収集]
  GPT-5.4 Thinking → 調査結果 → obsidian-vault/raw/
                                 ↓
                            knowledge-pipeline (--ingest → --compile)
                                 ↓
                            obsidian-vault/wiki/

[知識構造化]
  Claude → ai-os/knowledge/ (principles / playbooks / frameworks)

[実務実行]
  Claude が knowledge/ + obsidian-vault を参照
  → 設計・要件定義・提案
  → Codex に実装を投げる
  → Claude Code でレビュー・修正

[Eval]
  ai-os/evals/ で品質管理
  失敗 → ai-os/knowledge/failure_patterns/ に記録
```

---

## 7. タスク別AI運用

| タスク | 主担当 | 補助 |
|--------|--------|------|
| 技術調査・ベストプラクティス収集 | GPT-5.4 Thinking | - |
| 要件定義・課題設定 | Claude | - |
| 設計・アーキテクチャ | Claude | - |
| 実装（局所・短時間） | Claude Code | - |
| 実装（長時間・反復） | Codex | Claude Codeでレビュー |
| EDA設計 | Claude | - |
| EDAコード | Claude Code / Codex | - |
| 結果解釈・次仮説 | Claude | - |
| 提案ストーリー | Claude | GPT-5.4 Thinkingで事例収集 |
| 知識変換（原則化） | Claude | - |

---

## 8. セッション開始プロトコル

1. 対象プロジェクトの `CLAUDE.md` を読む
2. `SESSION_NOTES.md` を読む
3. 関連する `knowledge/` ファイルをロードする
4. 目的・制約・成功条件を1文で要約する
5. タスクに入る

---

## 9. 知識の優先度

| 優先度A（Claude に常に渡す） | 優先度B（案件開始時に渡す） | 優先度C（必要時のみ） |
|--------------------------|--------------------------|-------------------|
| knowledge/principles/    | work/clients/*/PROJECT.md | obsidian-vault/raw/ |
| knowledge/frameworks/    | DECISION_LOG.md          | meeting_notes/    |
| shared/standards/        | 案件固有の DATA_CONTRACT.md | 調査メモの草案    |

---

## 10. 最重要原則

1. 単一AI万能主義を捨てる
2. 知識は raw で持たず、原則・判断基準・手順・失敗例に圧縮する
3. 思考フレームを明示し、自由作文を減らす
4. 出力形式を固定する
5. eval を運用中核にする
6. 失敗ログを資産に変える
