# knowledge-pipeline 使い方

## 基本フロー

### 自動モード（推奨）
```
① python main.py --watch を起動しておく（常駐）
② Web Clipper でクリップ → raw/ に保存
③ 5秒後に自動で --ingest が走る（要約・インデックス化・ChromaDB 登録）
④ --query / --search で活用
```

### 手動モード
```
① Web Clipper でクリップ → raw/ に保存
② --ingest で要約・インデックス化 + ChromaDB 登録（1コマンドで完結）
③ --query / --search で活用
   └ --query の回答は自動で ChromaDB に登録されるので次回以降の検索でも使われる
```

---

## セットアップ

### Obsidian Web Clipper の保存先設定
クリップ先を `C:/workspace/ai-os/obsidian-vault/raw/` に設定する。

### 依存パッケージのインストール
```bash
cd C:/workspace/ai-os/knowledge-pipeline
pip install -r requirements.txt
```

### 環境変数
`.env` ファイルをプロジェクトルートに作成:
```
ANTHROPIC_API_KEY=sk-...
```

---

## コマンド一覧

### --ingest
raw/ の新規 .md を検出して Claude が1行要約 + タグを生成し、`raw/_INDEX.md` に追記する。

```bash
python main.py --ingest
```

生成される `raw/_INDEX.md`:
```markdown
| ファイル | タイトル | 要約 | タグ | 追加日 |
|---------|---------|-----|-----|-------|
| [[20260405_xxx]] | Transformerの量子化 | INT4でVRAM半減する手法 | LLM, 軽量化 | 2026-04-05 |
```

---

### --embed-only
vault 全体をスキャンして未登録ファイルを ChromaDB に追加する。`--ingest` の後に実行する。

```bash
python main.py --embed-only
```

短いdoc（1500語未満）は全文を1エントリとして登録。長いdocはチャンク分割。

---

### --query
質問に対してRAG検索 → 関連docの全文を読む → Claude が回答を生成 → `vault/reports/` に保存する。

```bash
python main.py --query "Transformerの量子化手法を比較したい"
python main.py --query "KaggleでLSTMを使う際のベストプラクティス" --top-k 8
```

回答は `vault/reports/qa_YYYYMMDD_HHMMSS_{slug}.md` に保存される。

---

### --search
キーワードAND検索。ターミナルにスニペット付きで結果を表示する。

```bash
python main.py --search "量子化 VRAM"
python main.py --search "Kaggle アンサンブル" --top-k 20
```

---

### --search-ui
ブラウザで使える検索UIを起動する。

```bash
python main.py --search-ui
# → http://127.0.0.1:8766 を開く
```

---

### --compile
vault 内の記事から `[[wikiリンク]]` を抽出し、コンセプトページ（`wiki/`）を自動生成する。
`wiki/_INDEX.md` も更新される。

```bash
python main.py --compile
python main.py --compile --compile-force   # 既存ページも再生成
python main.py --compile --compile-batch 20  # 1回に最大20ページ生成
```

記事中に `[[LLM]]` `[[量子化]]` のように書いておくと、そのコンセプトページが作られる。

---

### --lint
wiki の健全性チェックレポートを `vault/reports/lint_YYYY-MM-DD.md` に生成する。

```bash
python main.py --lint
```

検出内容:
- 孤立記事（wikiリンクもタグもない）
- 壊れたリンク（wiki/にページがない概念）
- 孤立コンセプト（wiki/にあるが記事から参照されていない）
- 新規コンセプト候補

---

### --report
指定トピックについてRAG検索 → Claude がレポートまたはMarpスライドを生成する。

```bash
python main.py --report "LLMの量子化手法まとめ"
python main.py --report "時系列予測の最新手法" --format marp  # Marpスライド
```

出力先: `vault/reports/report_YYYYMMDD_{slug}.md`

---

### --idea
テキストを Claude が整形して `vault/ideas/` に保存し、ChromaDB にも登録する。

```bash
python main.py --idea "Reservoir Computingをtabularデータに使えるか試してみたい"
```

---

### --context
RAG検索 → Claude が CONTEXT.md を生成する。コンペや業務の作業開始前に使う。

```bash
python main.py --context "時系列異常検知" --mode comp
python main.py --context "需給最適化" --mode work
```

---

### --analyze
知識グラフの定量分析を実行する。

```bash
python main.py --analyze
```

---

### --watch
raw/ を監視して、新規ファイルが来たら自動で --ingest を実行する（常駐プロセス）。

```bash
python main.py --watch                   # ingest のみ自動
python main.py --watch --auto-compile    # vault の変更でも compile を自動実行
```

`--auto-compile` を付けると：
- vault 内のファイル変更を検出 → 60秒のデバウンス後に `--compile` を自動実行
- Obsidian で `[[リンク]]` を書くと次のコンパイルでwikiページが自動生成される
- _INDEX.md のハッシュが変わっていなければ Claude API は呼ばれない（コスト節約）

---

## 推奨ルーティン

| タイミング | コマンド |
|-----------|---------|
| 作業中は常駐 | `--watch --auto-compile` |
| 週1回 | `--lint` |
| 調べたいとき | `--query` または `--search-ui` |
| コンペ・業務開始時 | `--context` |

---

## vault ディレクトリ構成

```
obsidian-vault/
  raw/
    _INDEX.md       ← --ingest が自動更新
    20260405_xxx.md ← Web Clipper でクリップした記事
  wiki/
    _INDEX.md       ← --compile が自動更新
    LLM.md          ← --compile が生成するコンセプトページ
    量子化.md
  inbox/            ← 未分類の一時置き場
  blogs/
  papers/
  notebooks/
  ideas/            ← --idea の保存先
  reports/          ← --query / --report / --lint の出力先
  _templates/       ← Obsidian テンプレート
```
