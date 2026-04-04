---
title: "RAG Design Principles"
type: framework
domain: rag
tags: [rag, retrieval, vector_search, knowledge_base]
created: 2026-04-05
source: "Azure AI / Anthropic / Google best practices"
---

## Summary
RAGは「入れたら賢くなる箱」ではない。
検索品質がシステム品質のほぼ全てを決める。
チャンク設計・メタデータ・再ランキングが本体。

## Core Principles
- ベクトル検索だけでは弱い。ハイブリッド検索が基本
- チャンク = 1チャンク1論点
- メタデータ設計が検索フィルタの精度を決める
- 引用可能性（どこから取ったか）を担保する
- 検索自体を評価できる eval を持つ

## Decision Rules
- docが短い（<1500語）: 全文を1エントリとしてembed
- docが長い（>=1500語）: チャンク分割（500語・50語オーバーラップ）
- 複数ソースにまたがる質問: hybrid search + reranker
- 特定プロジェクトの情報: metadata filterで絞る

## 推奨メタデータスキーマ
```yaml
id: ""
title: ""
type: principle | playbook | project_context | blog | paper
domain: ds | ml | pm | rag | coding | general
project: ""          # プロジェクト固有情報の場合
tags: []
created_at: ""
updated_at: ""
source: ""
confidence: high | medium | low
applicability: ""    # 適用条件
non_applicability: "" # 非適用条件
```

## Procedure（RAGシステム構築順）
1. チャンク設計（サイズ・境界・オーバーラップ）
2. メタデータスキーマ設計
3. ハイブリッド検索構築（vector + BM25）
4. リランカー追加（CrossEncoder等）
5. クエリ変換（query rewriting）
6. 引用出力の設計
7. Retrieval eval の構築
8. 継続的な品質モニタリング

## Anti-patterns
- ベクトル検索だけで完結させる
- チャンクサイズを考えずに固定値で分割
- メタデータなしで全文検索
- 検索結果の評価をしない
- 埋め込みモデルを日本語テキストで評価せずに使う

## Eval
- 必要な情報を引けているか（Recall）
- 不要な情報を混ぜていないか（Precision）
- 引用元が正しいか
- チャンク境界で文脈が切れていないか
