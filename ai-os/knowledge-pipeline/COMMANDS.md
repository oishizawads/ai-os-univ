# knowledge-pipeline コマンド一覧

## 前提

```bash
cd C:\workspace\knowledge-pipeline
conda activate knowledge-pipeline
```

---

## パイプライン全体像

```
収集                     保存                      活用
────────────────────     ────────────────────────  ────────────────────
RSS / note / arXiv  →   raw/   (整形前の原文)      --query      RAG検索
X (Nitter)          →   blogs/ (Claude整形済み)    --context    CONTEXT.md生成
                        papers/                    --compile    Wikiコンパイル
                        wiki/  (コンセプトページ)  --lint       健全性チェック
                        reports/ (レポート)         --report     包括レポート
```

---

## 基本実行

```bash
python main.py
```

**全工程一括**（収集 → raw保存 → 整形 → Vault保存 → embedding）。
毎日の定期実行に使う。新着なければ何もしない。

```bash
python main.py --collect-only   # 収集 + raw保存のみ（整形・保存はしない）
python main.py --embed-only     # Vault内の全.mdを再embedding
                                # 手動でmdを追加・編集したときに使う
```

---

## 収集系

### キーワード指定収集

```bash
python main.py --keyword "RAG"
python main.py --keyword "PatchTST 時系列"    # スペース区切りでAND検索
python main.py --add-keywords "FLAIR,ESN"    # デフォルトキーワードに追加して全工程実行
```

config.yaml の `filters.include_keywords` を無視して、指定キーワードだけでフィルタする。
スポット収集に使う（「このキーワードの記事を今すぐ集めたい」ケース）。

### コンペ専用収集

```bash
python main.py --comp "RSNA 2026"
```

全RSSフィードをコンペ名でフィルタして収集し、`vault/competitions/{slug}/` に保存する。
config.yaml の `competitions.active_competitions` に登録しておくと通常実行でも収集される。

---

## 検索・参照系

### RAG検索

```bash
python main.py --query "時系列予測"
python main.py --query "時系列予測" --top-k 10       # 取得チャンク数（デフォルト5）
python main.py --query "時系列予測" --output result.md  # ファイルに保存
```

ChromaDBに登録済みのチャンクをembedding検索して返す。
`--top-k` を上げると幅広い知識を引けるが、出力が長くなる。

### CONTEXT.md生成（Claude Codeへの文脈渡し）

```bash
python main.py --context "需給予測"                       # workモード（デフォルト）
python main.py --context "時系列異常検知" --mode comp     # コンペ用
python main.py --context "需給予測" --top-k 10            # 参照チャンク数を増やす
```

RAG検索 → Claude API でプロジェクト向けのCONTEXT.mdを生成して保存する。
Claude Codeのセッション開始時に読ませる用途。

**保存先の決定ルール:**
- `config.yaml` の `contexts.work` / `contexts.comp` にクエリと一致する `name` があればそのパスへ
- 一致しなければ `contexts/{mode}/{日付}_{slug}_context.md`

---

## Wiki コンパイル

整形済み記事の本文に含まれる `[[概念名]]` リンクを走査し、コンセプトページを自動生成する。

```bash
python main.py --compile
```

**動作:**
1. `blogs/` `papers/` `notebooks/` の全.mdから `[[wikilink]]` を収集
2. `wiki/{概念名}.md` が未存在のコンセプトを抽出
3. Claude API で各コンセプトのwikiページを生成（概要・詳細・関連概念・実装メモ）
4. `wiki/INDEX.md` を更新

```bash
python main.py --compile --compile-batch 20   # 1回に生成するページ数（デフォルト10）
                                               # 大量にあるときは数回に分けて実行
python main.py --compile-force                 # 既存ページも強制再生成（内容を刷新したいとき）
```

**生成されるファイル:**
```
vault/wiki/
  Transformer.md       # 概要・詳細・関連概念・実装メモ・参考文献
  RAG.md
  時系列予測.md
  ...
  INDEX.md             # 全コンセプト一覧（自動更新）
```

**費用目安:** コンセプト1件 ≈ $0.03（Claude Sonnet）。100件で約$3。

---

## Lint（Wiki健全性チェック）

```bash
python main.py --lint
```

Vault全体を走査して以下をチェックし、`vault/reports/lint_{日付}.md` にレポートを保存する。

| チェック項目 | 説明 | 推奨アクション |
|---|---|---|
| 孤立記事 | wikiリンクもタグもない記事 | 整形が不完全な可能性 → 手動確認 or 再整形 |
| 壊れたリンク | `[[概念名]]` が wiki/ に存在しない | `--compile` で生成 |
| 孤立コンセプト | wiki/ にあるが記事から参照ゼロ | 削除候補 or 記事側に追記 |
| タグ分布 | 上位タグと記事数の一覧 | アンバランスなら taxonomy を見直す |
| 新規コンセプト候補 | 2記事以上から参照されているがwikiページ未作成 | `--compile` で一括生成 |

**使い方のサイクル:**
```
--lint で壊れたリンク・候補を確認
  → --compile でまとめて生成
  → --lint で再チェック
```

---

## レポート生成

RAG検索 → Claude API で包括的なレポートを生成し `vault/reports/` に保存する。
`--context` より長く・深い内容になる（max_tokens: 4000）。

```bash
python main.py --report "RAGの実装手法"
python main.py --report "時系列予測の最新手法" --top-k 15   # 参照チャンク数を増やす
```

**Marpスライド形式で出力（発表・共有用）:**

```bash
python main.py --report "Transformer" --format marp
```

`---` で区切られたMarpスライドが生成される。ObsidianのMarpプラグインやVS Code拡張でそのままプレビュー・PDF化できる。

**保存先:**
```
vault/reports/
  report_20260403_RAGの実装手法.md     # 通常レポート
  slides_20260403_Transformer.md      # Marpスライド
```

**費用目安:** レポート1件 ≈ $0.05〜0.08（チャンク数・出力長による）。

---

## アイデア記録

```bash
python main.py --idea "Reservoir ComputingとRAGを組み合わせて長期記憶を実現する"
```

入力テキストをClaude APIで整形（背景・アイデア本文・実装メモ・関連概念）して `vault/ideas/` に保存し、embeddingも登録する。
後から `--query` や `--report` で呼び出せる。

---

## Vault・グラフ管理

```bash
python main.py --link-similar            # 類似度の高い記事間に自動でwikiリンクを張る
python main.py --link-similar --dry-run  # 変更せず確認だけ（何がリンクされるか確認）
python main.py --analyze                 # 知識グラフ定量分析レポートをVaultに保存
```

**`--link-similar` の動作:**
- ChromaDBのembeddingを使って各記事の類似記事を探す
- 類似度が `linking.similarity_threshold`（デフォルト0.75）以上なら `[[タイトル]]` リンクを追記
- `--compile` と組み合わせると、リンク先のwikiページも芋づる式に生成できる

---

## ブラウザ拡張用サーバー

```bash
python main.py --serve              # APIサーバー起動（http://127.0.0.1:8765）
python main.py --serve --port 9000  # ポート変更
```

EdgeのObsidian Web Clipper拡張機能から「Add to Vault」するときに事前に起動しておく。
Webページを手動でVaultに追加する用途。起動したままにしておいてよい。

---

## タスクスケジューラ（毎日自動実行）

```bash
# 登録（毎朝7:00に python main.py を自動実行）
schtasks /create /tn "knowledge-pipeline" /tr "cmd /c cd C:\workspace\knowledge-pipeline && conda run -n knowledge-pipeline python main.py" /sc daily /st 07:00

# 登録確認
schtasks /query /tn "knowledge-pipeline"

# 削除
schtasks /delete /tn "knowledge-pipeline"
```

---

## config.yaml 主要設定

### ソース設定

| 設定項目 | パス | 説明 |
|---|---|---|
| RSSフィード追加 | `sources.rss.feeds` | `name` / `url` / `type` を追記 |
| RSS全文取得（全体） | `sources.rss.fetch_full_content` | `true` でRSS抜粋でなく記事全文を取得してClaudeに渡す |
| RSS全文取得（個別） | `sources.rss.feeds[].fetch_full_content` | フィードごとに上書き可能。全体 `false` でも個別 `true` にできる |
| noteハッシュタグ | `sources.note.hashtags` | 収集するハッシュタグ一覧（例: `機械学習`） |
| noteユーザー | `sources.note.users` | フォローするnoteユーザーのURLネーム |
| X有効化 | `sources.x.enabled` | `true` にするとNitter RSS収集を開始（デフォルト `false`） |
| X検索クエリ | `sources.x.search_queries` | Nitter経由で検索するキーワード |
| Nitterインスタンス | `sources.x.nitter_instances` | 優先順に複数指定。死んでいたら次を試す |

### フィルタ・タグ

| 設定項目 | パス | 説明 |
|---|---|---|
| 収集キーワード | `filters.include_keywords` | いずれか1つでも含む記事を通す（空にすると全件） |
| 除外キーワード | `filters.exclude_keywords` | 含む記事を弾く |
| タグタクソノミー | `tags.taxonomy` | Claudeが選べるタグの候補リスト |

### Vault・出力

| 設定項目 | パス | 説明 |
|---|---|---|
| Vault保存先 | `vault.path` | Obsidianのルートフォルダ |
| raw保存先 | `vault.raw_dir` | 整形前の原文（デフォルト `raw`） |
| Wiki保存先 | `vault.wiki_dir` | `--compile` の出力先（デフォルト `wiki`） |
| レポート保存先 | `vault.reports_dir` | `--report` / `--lint` の出力先（デフォルト `reports`） |

### Claude・Embedding

| 設定項目 | パス | 説明 |
|---|---|---|
| モデル | `claude.model` | 整形に使うClaudeモデル |
| 入力上限 | `claude.max_input_chars` | 記事本文の最大文字数（デフォルト12000） |
| 出力上限 | `claude.max_tokens` | 整形出力のトークン上限（デフォルト2000） |
| 類似リンク閾値 | `linking.similarity_threshold` | デフォルト0.75（上げると厳しく、下げると多くリンクされる） |
| プロジェクト登録 | `contexts.work` / `contexts.comp` | `--context` の保存先をname一致で自動振り分け |
