---
title: NotebookLM Integration Workflow
type: standard
updated: 2026-05-03
---

# NotebookLM ワークフロー

## NotebookLM とは
Googleの AIリサーチツール。**ドキュメントをソースとして読み込み**、Q&A・要約・音声オーバービュー（ポッドキャスト形式）を自動生成する。

公式API なし。Google Drive / Google Docs からのソース取り込みが最もスムーズ。

---

## このワークスペースとの統合方法

### アーキテクチャ
```
ai-os/knowledge/           →  /notebooklm-export  →  Google Drive  →  NotebookLM
(principles/frameworks/playbooks/failure_patterns)          ↑
                                                    Google Drive MCP
                                                    (Claude に統合済み)
```

### Google Drive MCP の確認
Claude には `mcp__claude_ai_Google_Drive__authenticate` が統合されている。  
初回のみ認証が必要:
```
# Claude Code 内で実行
mcp__claude_ai_Google_Drive__authenticate
```

---

## /notebooklm-export コマンドの動作

`/notebooklm-export [topic]` を実行すると以下を行う:

1. **バンドル生成**: 指定トピックに関連するknowledgeファイルを収集
2. **マークダウン統合**: 1つのドキュメントに統合（NotebookLMが読みやすい形式）
3. **Google Driveへアップロード**: `AI-OS-NotebookLM/` フォルダに保存
4. **NotebookLMへの追加手順を提示**: URLとステップを案内

---

## 手動ワークフロー（MCP認証前）

```bash
# 1. エクスポートバンドルを生成
python C:/workspace/tools/notebooklm_export.py --topic "finance" --output export.md

# 2. Google Driveに手動アップロード
#    → drive.google.com → 「AI-OS-NotebookLM」フォルダ

# 3. NotebookLMで新しいノートブックを作成
#    → notebooklm.google.com
#    → 「ソースを追加」→「Google Drive」→ export.md を選択
```

---

## トピック別エクスポートの例

```bash
# 金融AI知識をNotebookLMへ
python C:/workspace/tools/notebooklm_export.py --topic finance

# 実験・コンペ戦略
python C:/workspace/tools/notebooklm_export.py --topic competition

# エージェント設計
python C:/workspace/tools/notebooklm_export.py --topic agents

# 全knowledge
python C:/workspace/tools/notebooklm_export.py --all
```

---

## NotebookLM での推奨活用

| 機能 | 使い方 |
|------|--------|
| **音声オーバービュー** | playbooks + principles を聞きながら復習 |
| **Q&A** | 「このワークスペースでVaRはどう計算する？」 |
| **スタディガイド** | failure_patterns からチェックリスト生成 |
| **ブリーフィング文書** | 新プロジェクト開始前の文脈把握 |

---

## 更新タイミング
- 新しいplaybook / framework を追加した後
- 月次レビューのタイミング
- 新コンペ・新案件を始める前
