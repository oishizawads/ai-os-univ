# Workspace Reference（CLAUDE.md 補足・オンデマンド参照）

> CLAUDE.md から分離した「常時は不要だが時々参照する」運用詳細。
> 自動ロードされない＝コンテキストを常時消費しない。必要なときだけ読む。

## フィードバックループ
委譲後に `/feedback` で品質を記録 → 週次集計でルーティングを改善する。
```bash
/feedback --model codex --task implementation --quality 4
python C:/workspace/tools/feedback_analyzer.py   # 集計
```
ログ: `ai-os/shared/standards/agent_feedback.csv`
仕様: `ai-os/shared/standards/feedback_loop.md`

## NotebookLM 連携
knowledge ファイルを音声・Q&A形式で活用する:
```bash
/notebooklm-export finance      # 金融AI系
/notebooklm-export competition  # コンペ戦略
/notebooklm-export --all        # 全ナレッジ
```
仕様: `ai-os/shared/standards/notebooklm_workflow.md`

## Helper Functions
- `reverse_string`: Reverses a given string. Located in `src/reverse_string.py`.

## AI 委譲（直接・手動運用）
自動ルーティング（`/route` / `task_router.py`）・ai-delegate（LangGraph）・`/orchestrate`・`/dispatch`・`/plan`・`/ultrawork` は **2026-06-19 に廃止**（精度の都合で手動運用に回帰し未使用だったため）。委譲は各モデルへ直接: `/codex-coder` / `/opencode-coder` / `/gemini-coder`。
判断の参考: `ai-os/knowledge/frameworks/model_routing.md`（legacy）

## AI 活用ベストプラクティス（2026年版）
### セキュリティ・ガードレール
- フレームワーク: `ai-os/knowledge/frameworks/ai_security_guardrails.md`
- 失敗パターン: `ai-os/knowledge/failure_patterns/ai_security_incidents.md`
- レビュー手順: `ai-os/knowledge/playbooks/ai_security_review.md`

### マルチエージェント協調
- フレームワーク: `ai-os/knowledge/frameworks/multi_agent_coordination.md`
- 既存統合: `ai-os/knowledge/frameworks/ankh_swarm_protocol.md`

### AI 出力バージョン管理
- フレームワーク: `ai-os/knowledge/frameworks/ai_output_versioning.md`
- 回帰テスト: `ai-os/evals/regression_cases/`

### コスト最適化
- フレームワーク: `ai-os/knowledge/frameworks/cost_optimization_patterns.md`
- 既存統合: `ai-os/shared/standards/rtk_guidelines.md`
- モデルルーティング: `ai-os/knowledge/frameworks/model_routing.md`

## AI 活用ワークフロー
AI 生成コードの検証・品質担保に関する仕様:
- 仕様書: `ai-os/shared/standards/ai_workflow_spec.md`
- タスクテンプレート: `ai-os/templates/task_spec_template.md`
- レビューチェックリスト: `ai-os/templates/review_checklist_template.md`
- パターンテンプレート: `ai-os/templates/pattern_template.md`
- 検証スクリプト: `ai-os/shared/scripts/ai_verify.py`
- CI パイプライン: `.github/workflows/ai-verify.yml`
- パターン集: `ai-os/knowledge/ai_patterns/`

AI 活用時のデフォルト手順:
1. タスク仕様をテンプレートで作成
2. AI に仕様を渡して生成
3. `ai_verify.py` でローカル検証
4. PR 作成 → CI パイプライン自動実行
5. 人間は重点箇所のみレビュー（チェックリスト使用）
6. 成功パターンをパターン集に記録
