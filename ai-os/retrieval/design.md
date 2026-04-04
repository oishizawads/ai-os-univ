# Retrieval Design

knowledge-pipeline の検索設計とチャンク戦略を記録する。

---

## 現在の構成（2026-04-05時点）

### Embedding
- モデル: `intfloat/multilingual-e5-large`（日本語・英語両対応）
- DB: ChromaDB（ローカル永続化）
- 戦略: **ハイブリッドembed**

### チャンク戦略

| doc長 | 戦略 | 理由 |
|-------|------|------|
| < 1500語（Web Clipperの記事が多い） | 全文を1エントリとしてembed | 文脈が切れない。doc全体のトピックを正確にembedできる |
| >= 1500語（論文・長文ノート） | 500語 / 50語オーバーラップでチャンク分割 | 局所トピックの検索精度を維持 |

### 検索戦略

- **ベクトル検索のみ**（BM25全件スキャンはスケール問題があり廃止）
- 検索後に `source_file` で重複排除（同一docの複数チャンクは最高スコアのみ）
- ヒットしたdocパスからディスクの全文mdを読み込んでLLMに渡す

### Q&Aフロー

```
--query "質問" 
  → ChromaDB で関連doc特定（top-K）
  → source_fileで重複排除
  → ディスクから全文読み込み
  → Claude API で回答生成（doc全文をコンテキストとして渡す）
  → vault/reports/ に保存
```

---

## メタデータスキーマ

ChromaDB に保存するメタデータ:

```python
{
    "source_file": "/path/to/doc.md",  # ファイルパス（重複排除のキー）
    "filename": "20260405_xxx.md",
    "title": "記事タイトル",
    "type": "blog | paper | notebook | idea | wiki",
    "published": "2026-04-05",
    "url": "https://...",
    "is_full_doc": True,  # 全文embedかチャンクembedか
}
```

---

## コスト試算（2026-04-05時点）

- Sonnet 4.6: $3/MTok (input)
- 1クエリあたり: top-5 docs × 平均2000トークン = 約10,000トークン ≈ 約4円
- 月250クエリ = 約1000円 → 許容範囲内

---

## 今後の改善候補

- [ ] クエリ変換（query rewriting）で検索精度向上
- [ ] 長いdocのチャンク境界を文章境界に合わせる（現在は語数ベース）
- [ ] doc種別（paper/blog/wiki）によるメタデータフィルタ
