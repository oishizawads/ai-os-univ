# /notebooklm-export — NotebookLM用ナレッジバンドルを生成する

ai-os/knowledge/ の内容をトピック別に1つのMarkdownファイルにまとめ、
NotebookLM へのインポート用として出力する。

## 使い方

```
/notebooklm-export [topic]
```

### トピック一覧
- `finance` — 金融AI系（FinceptTerminal, Vibe-Trading, QuantDinger, TradingAgents, dexter-jp など）
- `competition` — コンペ戦略（competition_strategy, vibe_coding, failure_patterns など）
- `agents` — エージェント設計（parallel_agent_workflow など）
- `research` — リサーチ手法（last30days, scientific-skills, matsuo-lab など）
- `all` — 全ナレッジ

## 実行

```bash
# トピック指定
python C:/workspace/tools/notebooklm_export.py --topic finance

# 全ナレッジ
python C:/workspace/tools/notebooklm_export.py --all

# 出力先を指定
python C:/workspace/tools/notebooklm_export.py --topic competition --output my_bundle.md
```

出力先: `ai-os/exports/<topic>_<date>.md`

## NotebookLM へのインポート手順

1. notebooklm.google.com を開く
2. 「新しいノートブック」を作成
3. 「ソースを追加」→「ファイルをアップロード」
4. 生成された .md ファイルを選択
5. または Google Drive へアップロードして「Google Drive」から追加

## Google Drive MCP 経由（自動アップロード）

Claude の Google Drive MCP が認証済みの場合、直接アップロード可能:
```
# Claude Code セッション内で実行
mcp__claude_ai_Google_Drive__authenticate
# 認証後、生成ファイルを AI-OS-NotebookLM/ フォルダへアップロード
```

## 推奨活用
- 新プロジェクト開始前のコンテキスト把握（Q&A機能）
- playbooks + principles の音声オーバービュー（通勤中に聴く）
- failure_patterns からのチェックリスト生成
- 月次レビュー時の知識棚卸し

## 参照
`ai-os/shared/standards/notebooklm_workflow.md`
