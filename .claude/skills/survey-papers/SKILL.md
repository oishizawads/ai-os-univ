---
name: survey-papers
description: 論文、過去解法、関連手法を調査して実務に落とす
---

# Survey Papers

## Purpose
テーマに関する論文、解法、定石を調査し、このプロジェクトで使える形に整理する。

## Subagent Orchestration
スキル起動直後に以下を**同時に**起動する。

**researcher** に渡すプロンプト:
```
[ユーザーのテーマ] について、論文・技術ブログ・公式ドキュメントを調査してください。
出力: Strong known approaches / Why they matter / Risks / Try now / Try later
```

コンペ文脈の場合は追加で **kaggle-researcher** も起動:
```
[コンペ名 or タスク種別] の Kaggle discussion / notebook / 上位解法を調査してください。
CV設計・特徴量・アンサンブル戦略に絞って整理してください。
```

両エージェント完了後、結果を統合して Output Format に従い最終サマリを出力する。

## Output Format
- 3-line summary
- Strong known approaches
- Why they matter here
- Risks / caveats
- Try now
- Try later
- Not worth trying now