---
name: meeting-log
description: 会議メモを要約し、保存と SESSION_NOTES 反映まで進める。
---

# Meeting Log

## Mission
会議メモを、決定事項と次アクションが追える形に整える。

## Workflow
1. 既存の `meeting_notes/` と `SESSION_NOTES.md` を必要範囲だけ確認する。
2. Raw notes から `topic / date / participants / decisions / action items` を抜く。
3. 必要なら `meeting-note-writer` に清書を依頼する。
4. `meeting_notes/YYYY-MM-DD_<topic>.md` へ保存する。
5. `SESSION_NOTES.md` に 1 行で反映する。
6. Action items に担当と期限がない場合は、その不足を明記する。

## Guardrails
- Raw notes を勝手に補完しすぎない。
- 決定事項と議論中の論点を分ける。
- Action items は担当、期限、内容を優先して残す。
- topic は短く検索しやすい名前にする。

## Output
- Saved note path
- Decisions summary
- Action items
- SESSION_NOTES update line
- Missing information
