# Research - CLAUDE.md

## Purpose
研究活動の管理。論文・実験・調査・発表資料。

## ディレクトリ構成
```
research/
  <テーマ名>/
    README.md       ← 研究概要・RQ・現状
    literature/     ← 論文メモ（obsidian-vault/papers/ からの抜粋）
    experiments/    ← 実験設計・結果
    notes/          ← 思考メモ・仮説
    outputs/        ← 発表資料・原稿
```

## Research Question の書き方
```
RQ: （1文で）
背景: なぜこれを問うのか
既存研究の空白: 何がまだわかっていないか
自分のアプローチ: どう答えるか
```

## AIの使い分け
- 論文調査・関連研究整理 → `survey-papers`
- 実験設計 → `experiment-planner`
- 結果の解釈・次仮説 → Claude との壁打ち
- 発表資料 → 構成を Claude、内容は自分

## 論文読み方
1. Abstract・Conclusion を読んで価値判断
2. 価値があれば `obsidian-vault/papers/` にクリップ
3. `knowledge-pipeline --ingest` で取り込む
4. 重要な知見は `ai-os/knowledge/` に昇格
