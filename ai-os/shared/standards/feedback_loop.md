---
title: Agent Feedback Loop — 仕様と運用
type: standard
updated: 2026-05-03
---

# Agent Feedback Loop

## 目的
外部モデル（Codex / Gemini / OpenCode / Hermes / local-coder）への委譲結果を記録し、  
ルーティング精度を継続的に改善する。

---

## ログフォーマット

ファイル: `ai-os/shared/standards/agent_feedback.csv`

```csv
date,task_type,model,quality,tokens_saved,what_worked,what_failed,notes
2026-05-03,implementation,codex,4,high,correct output first try,,multi-file refactor
```

### フィールド定義

| フィールド | 型 | 説明 |
|------------|-----|------|
| `date` | YYYY-MM-DD | 委譲日 |
| `task_type` | str | implementation / research / reasoning / analysis / review / snippet |
| `model` | str | codex / gemini / opencode / hermes / local |
| `quality` | 1-5 | 1=完全失敗, 3=要修正, 5=完璧 |
| `tokens_saved` | high/med/low | Claudeトークン節約量の感触 |
| `what_worked` | str | うまくいった点 |
| `what_failed` | str | 失敗・要修正だった点 |
| `notes` | str | 自由記述 |

---

## 記録方法

```bash
# /feedback コマンド（.claude/commands/feedback.md）
/feedback --model codex --task implementation --quality 4 --worked "first-pass correct" --failed "" --notes "multi-file OK"

# または直接Pythonスクリプト
python C:/workspace/tools/feedback_logger.py \
  --model opencode --task snippet --quality 5 --tokens-saved high
```

---

## 週次レビュー（/weekly-review 時に実行）

以下を集計:
1. モデル別の平均品質スコア
2. タスクタイプ別の最高パフォーマンスモデル
3. quality <= 2 だったケースのパターン分析
4. ルーティング変更提案 → `ai-os/knowledge/frameworks/model_routing.md` を更新

集計スクリプト: `python C:/workspace/tools/feedback_analyzer.py`

---

## フィードバックループの全体図

```
タスク委譲
    ↓
モデルが実行
    ↓
Claude がレビュー（品質判断）
    ↓
/feedback で記録 → agent_feedback.csv
    ↓
週次集計 (feedback_analyzer.py)
    ↓
モデル × タスク別スコア表
    ↓
model_routing.md のルーティング更新
    ↓
次回の委譲判断が改善される ← ループ
```

---

## ルーティング改善トリガー

以下の条件でルーティングを見直す:
- 同じモデル × タスクタイプで quality <= 2 が3回連続
- 別モデルの同タスクで quality >= 4 が続く
- 新モデルが追加された（ルーティング表の更新が必要）
