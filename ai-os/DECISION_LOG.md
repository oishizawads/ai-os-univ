# Decision Log

重要な技術的・設計的意思決定を記録する。
「なぜそうしたか」が後から分かるようにする。

フォーマット: `## YYYY-MM-DD | タイトル`

---

## 2026-04-05 | knowledge-pipeline の自動収集を廃止

**Decision:** RSS/note/arxiv の自動収集を廃止し、Obsidian Web Clipperによる手動収集に切り替えた

**Why:** 自動収集はノイズが多く、品質管理が難しかった。手動収集の方が必要な情報を確実に取れる

**Trade-off:** 収集量は減るが、質が上がる。月1000円以内のAPIコストを維持できる

---

## 2026-04-05 | ChromaDB RAG を doc単位検索に変更

**Decision:** チャンク単位での返却をやめ、ChromaDBでdocを特定してからディスクの全文を読む方式に変更

**Why:** チャンク分割で文脈が切れる問題があった。個人KB規模（数百〜数千件）ではdoc全文をLLMに渡しても許容コスト範囲内

**Trade-off:** 1クエリあたりのトークン増加（約2円→20円程度）。月500クエリ以内なら月1000円以内

**Rule:** 短いdoc（<1500語）は全文embed、長いdoc（>=1500語）はチャンク分割

---

## 2026-04-05 | ai-os/knowledge/ を新規作成

**Decision:** ai-os/ 以下に knowledge/ ディレクトリを追加。原則・プレイブック・フレームワークを構造化して管理

**Why:** raw情報（メモ・ブログ）をそのまま保存するより、Claudeが判断に使える形（Decision Rules・Anti-patterns・Eval付き）に変換して保存する方が価値が高い

**Scope:** ai-os/knowledge/ = 自分でキュレーションした構造化知識。obsidian-vault/ = Web Clipperで収集した外部情報。この2つは別物

---

<!-- 新しい決定はここに追記 -->
