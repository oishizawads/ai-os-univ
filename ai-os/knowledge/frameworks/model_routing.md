---
title: Model Routing Framework
type: framework
updated: 2026-05-05
---

# Model Routing Framework

> **Status (2026-06-21): 一部 legacy。** 自動ルーター（Dynamic Task Router / `task_router.py` / `/route`）と無料ローカルrunner（Hermes / local-coder）は撤去済み。現行の正典は root `CLAUDE.md` と `.claude/REFERENCE.md`。以下は核心原則と、現存する委譲先（OpenCode / Gemini / Codex / decision-lab）に読み替えて使う。

## 核心原則
**Claude 直接実行が既定。** 設計・判断・実装・統合・最終判断まで Claude が一貫して担う。

委譲（OpenCode / Gemini / Codex）は**任意の escape hatch**。発火するのは ①ユーザーが明示的に他モデルへ振った時 ②量産・並列・トークン/スループットに実利がある時のみ。委譲は必須ではなく、いつでも使える選択肢。

---

## Dynamic Task Router — 撤去済み (2026-06-21)

> 2026-05-05 に試した自動ルーティング（`/route`・`task_router.py`・`status_collector.py`・`task_classifier.py`・`scoring_engine.py`）は精度不足のため撤去した。委譲は直接コマンド（`/opencode-coder` / `/gemini-coder` / `/codex-coder`）に一本化。

---

---

## トークンコスト階層

| Tier | モデル | コスト | 呼び出し方 |
|------|--------|--------|------------|
| 🟡 Low  | OpenCode Go (qwen3.6-plus via opencode-go) | 低 | `python C:/workspace/tools/opencode_coder.py "<prompt>"` |
| 🟡 Low  | Gemini CLI (gemini-2.5-flash / gemini-3) | 低 | `python C:/workspace/tools/gemini_coder.py "<prompt>"` |
| 🔴 High | Claude Code (現行モデルは root `CLAUDE.md` 参照) | 高 | — (自分自身・既定の実行者) |
| ⚠️ 制限 | **Codex (gpt-5.4)** read-only | 週次制限あり | `python C:/workspace/tools/codex_coder.py "<prompt>"` |

**ルール: 🔵 既定は Claude 直接実行。** 上の Tier は委譲する場合の選択肢であって、Claude を避ける理由ではない。
**⚠️ Codexは利用制限あり。実案件レビュー・重要度高タスクに限定して使用する。**

### Codex 使用条件
- 実案件（クライアント向け）のコードレビュー
- 本番影響あり・セキュリティ関連の実装
- OpenCode / Gemini のフォールバック（明らかに品質不十分な場合のみ）

### 委譲する場合の担当（任意）
- **実装の委譲** → OpenCode Go（高速・制限なし）
- **リサーチ・ドキュメント調査の委譲** → Gemini（広域検索が得意）

---

## タスク別ルーティング決定木

```
タスクを受け取る
│
├─ 「何をすべきか」の設計・判断・合成？
│   └─→ Claude (自分) ✅ 代替不可
│
├─ コーディング
│   ├─ 実装全般（既定）
│   │   └─→ Claude 直接 ← まずここ
│   ├─ 量産・並列・トークン実利がある時のみ委譲
│   │   └─→ 🟡 OpenCode Go (/opencode-coder)
│   ├─ 委譲のセカンド or 複数ファイル大規模
│   │   └─→ 🟡 Gemini (/gemini-coder)
│   ├─ 実案件レビュー・本番影響あり・セキュリティ
│   │   └─→ ⚠️ Codex (/codex:rescue) ← 制限あり、要節約
│   └─ コードレビュー・最終承認
│       └─→ Claude (自分) ✅ 代替不可
│
├─ リサーチ・検索
│   ├─ Webリサーチ・ドキュメント検索・広域コード調査
│   │   └─→ 🟡 Gemini (/gemini-coder または CLI)
│   ├─ 30日間トレンド・SNSコンセンサス
│   │   └─→ /last30days <topic>
│   └─ 論文・既知解法の調査
│       └─→ /survey-papers
│
├─ 推論・アイデア出し
│   └─ 構造化された不確実性分析（複数仮説）
│       └─→ decision-lab
│
├─ 知識まとめ・音声要約
│   └─→ /notebooklm-export → NotebookLM
│
└─ データサイエンス分析
    ├─ EDA・可視化・仮説整理
    │   └─→ data-analyst agent
    ├─ 実験設計・優先順位付け
    │   └─→ experiment-planner agent
    └─ 予測・因果・モデル比較
        └─→ decision-lab
```

---

## タスクサイズ閾値（目安）

| サイズ | 特徴 | 推奨モデル |
|--------|------|------------|
| XS | 1関数・1クエリ・docstring | OpenCode Go |
| S | 1ファイル・明確な仕様 | OpenCode Go |
| M | 複数ファイル・要テスト | Codex |
| L | 設計判断あり・リーク可能性あり | Claude + Codex |
| XL | アーキテクチャ変更・横断影響 | Claude のみ |

---

## 委譲テンプレート（Claude → 他モデル）

```
# 委譲時に含める情報:
1. タスクの目的（1行）
2. 入力ファイル / データの場所
3. 期待する出力形式
4. 制約（言語、ライブラリ、行数上限）
5. 評価基準（何をもって成功とするか）
```

委譲後はClaude自身がレビューし、`/feedback` でスコアを記録する。

---

## フィードバックループとの連携

委譲結果を `ai-os/shared/standards/agent_feedback.csv` に記録する。
詳細: `ai-os/shared/standards/feedback_loop.md`

週次レビュー時にルーティング精度を確認し、このファイルを更新する。
