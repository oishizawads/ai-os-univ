# log-meeting

## Objective
ミーティングのログを残す。議論・決定・アクションアイテムを構造化して記録する。

## When to Use
- ミーティング直後
- ミーティング前に議事録テンプレを作りたいとき
- ミーティングメモを整理したいとき

## Process

### Step 1: 記録場所を確認
現在のプロジェクト種別に応じて出力先を決める。
- コンペ: `meeting_notes/YYYY-MM-DD_<topic>.md`
- 実務案件: `meeting_notes/YYYY-MM-DD_<topic>.md`
- 社内: `work/company/meeting_notes/YYYY-MM-DD_<topic>.md`

### Step 2: 議事録を構造化
ユーザーから渡された生メモを以下フォーマットに整理する。
`meeting-note-writer` エージェントを使って構造化すること。

### Step 3: ファイルに保存
整理した議事録を該当ディレクトリに保存する。

### Step 4: SESSION_NOTES.md を更新
`SESSION_NOTES.md` の末尾に以下を追記する。
```
- [YYYY-MM-DD] MTG: <topic> → <決定事項1行>
```

## Output Format

```markdown
# Meeting Note - {date} {topic}

## Attendees
-

## Objective
-

## Discussion
-

## Decisions
- [ ] 

## Action Items
| Who | What | By When |
|-----|------|---------|
|     |      |         |

## Next Meeting
-

## Raw Notes
(元のメモをそのまま保存)
```

## Hard Rules
- Action Items は必ず Who / What / By When を埋める
- 決定事項と未決事項を分ける
- 「なんとなく話した」は Raw Notes に残す
