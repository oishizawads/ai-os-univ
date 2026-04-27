---
name: bug-investigation
description: 例外や不具合の原因を切り分ける
---

# Bug Investigation

## Purpose
不具合や例外発生時に、原因候補を複数出し、最短の切り分け手順を作る。

## Workflow
1. Symptom を要約する
2. 再現条件を確認する
3. 入力・設定・分割・保存物・依存関係を疑う
4. **error-analyzer** を起動しながら、Claude 自身も並列で仮説を生成する:
   ```
   以下のエラー / 異常挙動について原因仮説を最低3つ挙げ、
   最短の triage order を出してください。
   [エラーメッセージ・スタックトレース・再現条件を貼る]
   ```
5. error-analyzer の出力と Claude の仮説を統合し、重複除去・優先順位付けを行う
6. 最短の triage order を出す
7. 再発防止策を提案する

## Output Format
- Symptom summary
- Hypothesis 1
- Hypothesis 2
- Hypothesis 3
- Fastest triage order
- Prevention