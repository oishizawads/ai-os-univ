# Skill: meeting-log

## Purpose
ミーティングをログとして残す一連のワークフロー。
メモを渡すだけで、議事録作成・ファイル保存・SESSION_NOTES 更新まで行う。

## Trigger
ユーザーが「ミーティングのメモ」「mtgログ」「議事録」と言ったとき。
または `/log-meeting` コマンドが呼ばれたとき。

## Phases

### Phase 0: コンテキスト確認
1. 現在のプロジェクトを特定する（CWD または ユーザー発言から）
2. `meeting_notes/` ディレクトリの存在を確認（なければ作成）
3. ミーティングの日付とトピックをユーザーに確認（不明な場合のみ）

### Phase 1: 議事録生成
1. `meeting-note-writer` エージェントにメモを渡して構造化
2. 出力を確認してユーザーに提示

### Phase 2: ファイル保存
1. ファイル名: `meeting_notes/YYYY-MM-DD_<topic>.md`
   - topic はスペースをハイフンで置換、日本語可
2. ファイルを作成

### Phase 3: SESSION_NOTES.md 更新
1. 該当プロジェクトの `SESSION_NOTES.md` 末尾に追記:
   ```
   - [YYYY-MM-DD] MTG: {topic} → {decisions_1line}
   ```
2. decisions_1line は「決定事項」のうち最重要1件を1行で

### Phase 4: アクション確認
1. Action Items の担当者を確認
2. Codex に振れるものがあれば提案する

## Output
- 保存したファイルパスを伝える
- Action Items を番号付きリストで再掲する
- 次のアクションを明示する

## Hard Rules
- Raw Notes は必ず残す（元メモを消さない）
- Phase 0 のコンテキスト確認を省略しない
- Action Items が空の場合は「アクションなし」と明示する
