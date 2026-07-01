# /feedback — エージェント委譲結果を記録する

外部モデル（Codex / Gemini / OpenCode）への委譲後にフィードバックを記録する。
フィードバックループを回してルーティング精度を改善するためのコマンド。

## 使い方

```
/feedback --model <model> --task <task_type> --quality <1-5> [options]
```

### 必須パラメータ
- `--model`: codex / gemini / opencode
- `--task`: implementation / research / reasoning / analysis / review / snippet
- `--quality`: 1（完全失敗）〜 5（完璧）

### オプション
- `--tokens-saved`: high / med / low（Claudeトークン節約量の感触）
- `--worked`: うまくいった点（短い説明）
- `--failed`: 失敗・要修正だった点
- `--notes`: 自由記述

## 実行方法

```bash
python C:/workspace/tools/feedback_logger.py \
  --model codex \
  --task implementation \
  --quality 4 \
  --tokens-saved high \
  --worked "first-pass correct, no revision needed" \
  --failed "" \
  --notes "multi-file refactor across 3 files"
```

## 集計・改善提案の確認

```bash
# 全期間の集計
python C:/workspace/tools/feedback_analyzer.py

# 特定日以降
python C:/workspace/tools/feedback_analyzer.py --since 2026-05-01
```

## ログの場所
`ai-os/shared/standards/agent_feedback.csv`

## 参照
- ルーティング決定木: `ai-os/knowledge/frameworks/model_routing.md`
- フィードバックループ仕様: `ai-os/shared/standards/feedback_loop.md`
