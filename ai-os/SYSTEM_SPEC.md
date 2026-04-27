# AI OS — システム仕様書

> 対象読者: このシステムを使う自分・受け取った人  
> 目的: 「何ができるか」「どこに金がかかるか」「どう始めるか」を明確にする

---

## 0. はじめに（このリポジトリを受け取った人へ）

### 必要なもの

| ツール | 用途 | 入手先 |
|--------|------|--------|
| Claude Code（CLI） | メインのAI操作環境 | [claude.ai/code](https://claude.ai/code) |
| Python 3.10+ | knowledge-pipeline の実行 | python.org |
| Obsidian（任意） | ノート管理・Web Clipper | obsidian.md |
| Git | バージョン管理 | git-scm.com |

### セットアップ手順

#### 1. リポジトリを clone する

```bash
git clone https://github.com/oishizawads/-workspace-template-ai-os-.git workspace
cd workspace
```

#### 2. ディレクトリ構造を確認する

```
workspace/
  ai-os/
    knowledge-pipeline/   ← 知識収集・検索パイプライン
    knowledge/            ← 構造化知識（フレームワーク等）
    work/company/         ← 業務ナレッジ（テンプレート）
    CLAUDE.md             ← Claude Code への指示ファイル
    SYSTEM_SPEC.md        ← このファイル
```

#### 3. knowledge-pipeline をセットアップする

```bash
cd ai-os/knowledge-pipeline

# 依存関係をインストール
pip install -r requirements.txt

# APIキーを設定（.env を作成）
cp .env.example .env
# .env を開いて ANTHROPIC_API_KEY を自分のキーに書き換える

# config.yaml を自分の環境に合わせて編集
#   vault.path: Obsidian vaultのパスに変更
```

#### 4. config.yaml を編集する

`ai-os/knowledge-pipeline/config.yaml` を開き、以下を自分の環境に合わせて変更する：

```yaml
vault:
  path: "/path/to/your/obsidian-vault"  # ← 自分のObsidian vaultパスに変更
```

#### 5. CLAUDE.md のパスを更新する

`ai-os/CLAUDE.md` の Knowledge Resources セクションにあるパスを、自分の環境に合わせて書き換える。

#### 6. Claude Code を起動する

```bash
# workspace/ ディレクトリで起動
claude
```

Claude Code が `CLAUDE.md` を自動で読み込み、AI OSとして動作し始める。

### APIキーの取得

- **Anthropic API Key**: [console.anthropic.com](https://console.anthropic.com) でアカウント作成 → API Keys → Create key

---

---

## 1. システム全体像

```
┌─────────────────────────────────────────────────────────┐
│                   Claude Code（ターミナル）               │
│  ・ファイルを直接読む（Read/Grep/Glob ツール）             │
│  ・コードを書く・編集する                                  │
│  ・あなたと会話しながら作業する                            │
└──────────┬──────────────────────────────────────────────┘
           │ 直接参照（API不要）
           ▼
┌──────────────────────────────┐
│  knowledge/                  │  ← 自分でキュレーションした知識
│    principles/               │     Claude Code が作業開始時に読む
│    frameworks/               │
│    playbooks/                │
│    failure_patterns/         │
└──────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                   knowledge-pipeline                      │
│  （別プロセス。Claude Code とは独立して動く）              │
│                                                          │
│  --ingest    [Claude API使用] 記事をタグ付け・要約・登録  │
│  --query     [Claude API使用] RAG検索 + Claude が回答    │
│  --search    [API不要]        ベクトル検索のみ            │
│  --search-ui [API不要]        ブラウザで検索UI            │
│  --watch     [API使用]        raw/ を監視して自動ingest  │
│  --reindex   [API不要]        ChromaDB を再構築          │
└──────────┬───────────────────────────────────────────────┘
           │ 保存先
           ▼
┌──────────────────────────────┐
│  obsidian-vault/ (iCloud)    │
│    raw/         クリップ原文  │
│    wiki/        生成wiki     │
│    reports/     --query結果  │
│    _INDEX.md    記事目次      │
│  ChromaDB       ベクトルDB   │
└──────────────────────────────┘
           ↑
           │ iPhone Web Clipper
```

---

## 2. Claude Code（ターミナル）が何をしているか

### できること

| 操作 | 仕組み | コスト |
|------|--------|--------|
| ローカルファイルを読む | Read/Grep/Glob ツールで直接アクセス | Claude Code の月額に含まれる |
| knowledge/ を参照して判断する | 同上 | 同上 |
| コードを書く・編集する | Edit/Write ツール | 同上 |
| ターミナルコマンドを実行する | Bash ツール | 同上 |
| obsidian-vault/ の記事を読む | ファイルを直接 Read | 同上 |
| reports/ の RAG結果を読む | ファイルを直接 Read | 同上 |

### やっていないこと

- **ChromaDB を自動で検索していない**（knowledge-pipeline を呼んでいない）
- **リアルタイムで Web 検索していない**（明示的に WebSearch ツールを使う場合のみ）

### Claude Code がファイルを参照する流れ

```
あなた: 「実験設計してほしい」
         ↓
Claude Code: knowledge/frameworks/experiment_design.md を読む
             knowledge/frameworks/issue_driven.md を読む
             → これらを文脈として回答を生成する
```

---

## 3. knowledge-pipeline が何をしているか

Claude Code とは **独立した別プロセス**。ターミナルで手動実行するか `--watch` で常駐させる。

### --ingest（記事の取り込み）

```
raw/ の .md ファイルを読む
    ↓ Claude API（claude-sonnet-4）呼び出し
タグ付け・要約を生成
    ↓
_INDEX.md に追記
ChromaDB にベクトル登録（ローカル実行）
```

**課金ポイント**: Claude API 呼び出し（1記事あたり約 $0.01〜0.03）

### --query（RAG検索 + 回答生成）

```
質問文をベクトル化（ローカル）
    ↓
ChromaDB から関連記事を上位5件取得（ローカル）
    ↓ Claude API 呼び出し（記事全文 + 質問を渡す）
Claude が回答を生成
    ↓
obsidian-vault/reports/ に .md で保存
```

**課金ポイント**: Claude API 呼び出し（1回あたり約 $0.05〜0.10）  
入力トークン: 検索ヒット記事の全文 × 5件 ≈ 15,000〜20,000 tokens  
出力トークン: 回答文 ≈ 1,000〜2,000 tokens

### --search / --search-ui（ベクトル検索のみ）

```
質問文をベクトル化（ローカル）
    ↓
ChromaDB から関連記事を取得（ローカル）
    ↓
ファイル名・スニペットを表示するだけ
```

**課金なし**。Claude API を一切使わない。

### --watch（常駐監視）

```
raw/ を監視（ファイル追加を検知）
    ↓ 新ファイル検出
--ingest と同じ処理を自動実行
```

**課金ポイント**: 新ファイル検出のたびに --ingest と同額の API コール

---

## 4. コスト全体像

### 月額固定費

| サービス | 費用 | 内容 |
|---------|------|------|
| Claude Code（ターミナル） | Anthropic の Claude Code プラン | ターミナルでの会話・ファイル操作すべて |
| iCloud | 無料枠（5GB）以内なら無料 | vault の同期 |
| 埋め込みモデル | 無料 | multilingual-e5-large をローカル実行 |
| ChromaDB | 無料 | ローカル実行 |

### 従量課金（Claude API）

| 操作 | 1回あたり費用 | 使用モデル |
|------|-------------|-----------|
| --ingest 1記事 | $0.01〜0.03 | claude-sonnet-4 |
| --query 1回 | $0.05〜0.10 | claude-sonnet-4 |
| --watch（記事1件自動処理） | --ingest と同額 | claude-sonnet-4 |
| --search / --search-ui | **$0** | なし |
| --reindex | **$0** | なし |
| knowledge/ 参照 | **$0** | なし（Claude Code で読むだけ） |

### 月間コスト試算

| 使い方 | 月額目安 |
|--------|---------|
| クリップ 30記事 / 月、検索は --search のみ | 約 $0.30〜0.90 |
| クリップ 30記事 + --query 10回 | 約 $0.80〜1.80 |
| --watch 常時起動 + 大量クリップ（100記事） | 約 $1〜3 |

---

## 5. Claude Code が knowledge-pipeline の結果を使う方法

Claude Code は ChromaDB を直接見ない。以下の方法で連携する。

### 方法A: reports/ を読む（推奨）

```bash
# 先にRAG検索しておく（従量課金 $0.05〜0.10）
python main.py --query "LLMエージェントの設計パターン"
# → reports/qa_20260405_....md に保存される

# Claude Code がそのファイルを読んで作業に活用する
```

### 方法B: --search-ui で探して直接ファイルを渡す（無料）

```bash
# ブラウザで検索（無料）
python main.py --search-ui
# → 関連記事のファイルパスがわかる

# Claude Code に「このファイルを参照して」と伝える
# → Claude Code が raw/ のファイルを直接 Read する
```

### 方法C: knowledge/ を直接参照（常時・無料）

Claude Code はセッション開始時に自動で以下を読む（CLAUDE.md の設定による）:
- `knowledge/frameworks/` — 思考フレームワーク
- `knowledge/principles/` — 判断原則
- `knowledge/playbooks/` — 手順

これらは API コストなしで参照される。

---

## 6. コストを最小化する運用

```
クリップした記事を活用したい
    ↓
[無料] --search-ui でキーワード検索
    → ヒットしたファイルを「このファイル読んで」と Claude Code に渡す

[有料 $0.05] どうしても要約・統合回答が欲しい場合だけ --query を使う

タグ付けは週1回まとめて --ingest（daily でやると記事数 × $0.02 かかる）
```

---

## 7. まとめ

| 疑問 | 答え |
|------|------|
| Claude Code はローカルファイルを見るか | **見る**。Read/Grep で直接アクセス |
| Claude Code は RAG 検索を自動でするか | **しない**。knowledge-pipeline とは別プロセス |
| タグ付けはどこで金がかかるか | --ingest / --watch 実行時（Claude API） |
| 検索だけなら無料か | **無料**。--search / --search-ui はAPI不使用 |
| どう連携するか | reports/ にファイルを置いて Claude Code に読ませる |
