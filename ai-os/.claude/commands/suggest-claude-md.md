# suggest-claude-md

## Objective
直近の作業内容から、`CLAUDE.md` に追加・修正すべき運用ルール候補を抽出する。

## When to Use
- セッションの終わり
- 同じミスや確認事項が繰り返された時
- 新しい運用ルールが暗黙知として見え始めた時
- 「これ毎回言ってるな」と感じた時

## Inputs
以下を優先的に参照する。
1. 現在の `CLAUDE.md`
2. `SESSION_NOTES.md`
3. 直近の `.steering/`
4. 直近の `result.md`, `meeting_notes`, `daily_reports`
5. 今回のやり取りで得られた再利用可能な学び

## What to Extract
次のどれかに当てはまるものだけを候補にする。
- 再現性に効くルール
- 品質管理に効くルール
- 作業順序に効くルール
- エラー予防に効くルール
- Claude と Codex の役割分担に効くルール
- 競技または業務で繰り返し使えるルール

## Hard Rules
- 一時的な事情は候補にしない
- 案件固有すぎる内容はグローバルルールにしない
- 既存ルールと重複する場合は「追記」ではなく「統合案」を出す
- 抽象論は禁止。具体的な文として書く

## Output Format

### Candidate Rules
1. Rule:
   Why:
   Scope: global / competition / client-project / company
   Where to add:
   Replace existing?: yes / no

2. Rule:
   Why:
   Scope:
   Where to add:
   Replace existing?: yes / no

### Suggested Patch
`CLAUDE.md` に追記・修正する文面を、そのままコピペ可能な形で出す。

### Keep / Reject
- Keep:
- Reject:
- Why rejected:

## Final Instruction
候補は最大5個まで。数より質を優先すること。