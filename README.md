# AI-OS

**エージェント駆動のデータサイエンス・ワークスペース** — LLMエージェント（Claude Code + Codex）を「PM」と「エンジニア」に分業させ、機械学習コンペ・研究・実務を *再現可能* に回すための自作OSです。

> 「単発のAI出力を信用しない」「探索コードと本番コードを分ける」「判断は人間、実行はエージェント」を原則に、データサイエンスの作業環境そのものを設計しました。

---

## なにを解決するか

データサイエンスの実作業は、コードだけでなく **実験管理・意思決定の記録・知識の蓄積・複数AIの使い分け** が品質を左右します。AI-OS はそれらを 1 つのワークフローに統合します。

| 課題 | AI-OS のアプローチ |
|------|------------------|
| 実験の再現性が崩れる | 実験台帳・`SESSION_NOTES`・`.steering/` をテンプレ化し、セッションを跨いで継続 |
| AI出力を鵜呑みにしてしまう | Claude=設計/レビュー、Codex=実装 と役割を分離し、相互検証を前提化 |
| 知識が流れて消える | Web記事を収集→検索→wiki化する **ナレッジパイプライン（RAG）** |
| 作業の型が毎回バラつく | コンペ/実務用の **skill・command・agent ライブラリ** を再利用 |

---

## アーキテクチャ

```
ai-os/
  competitions/        # MLコンペ（実験台帳・検証ルール・baseline）
  work/                # 実務（社内OS・PoC・再利用資産）※内容はテンプレートのみ公開
  knowledge-pipeline/  # Web記事の収集→RAG検索→wiki化（chromadb + sentence-transformers + FastAPI）
  knowledge/           # 構造化知識（principles / playbooks / frameworks / failure_patterns）
  templates/           # コンペ/実務プロジェクトの雛形
  shared/              # 共通プロンプト・標準・スニペット
  .claude/             # agents / commands / skills 定義
  hooks/               # セッション開始・実験台帳・日次レポート自動化
```

### マルチエージェントの分業
- **Claude** = PM（設計・判断・レビュー・統合）
- **Codex / OpenCode / Gemini** = エンジニア（実装・実験・重い処理）
- **decision-lab** = 不確実性の高い分析の多経路検証

---

## 主な構成要素

- **再現可能なコンペ/実験ワークフロー** — 目的・検証戦略・リーク risk・成果物パスを最初に固定し、最小の変更で1仮説ずつ検証
- **ナレッジパイプライン (RAG)** — `feedparser`/`arxiv`/`beautifulsoup4` で収集 → `chromadb` + `sentence-transformers` で意味検索 → Obsidian wiki へ書き出し
- **skill / command ライブラリ** — `/eda`, `/baseline`, `/review-exp`, `/submit` などデータサイエンス作業の定型を slash command 化
- **hooks による自動化** — セッション開始時にコンテキストを自動表示、実験ログを自動記録

## 技術スタック
`Python 3.12` / `uv` / `FastAPI` / `chromadb` / `sentence-transformers` / `networkx` / `watchdog` / `Claude Code` / `Codex`

---

## このリポジトリについて
- 実際のクライアント案件・実験データ・秘匿情報は含みません（`work/` 配下は構造テンプレートのみ）。
- 名古屋市立大学 データサイエンス学部の学生として、コンペ・研究・実務を一人で回すために設計・運用しているシステムの **公開テンプレート版** です。
