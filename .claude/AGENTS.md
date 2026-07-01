# Current Override

Follow `WORKFLOW_DIAGRAM.md` and `../AGENTS.md` for current operation.
The active rule is direct execution by default: Codex/Claude should perform
design, implementation, analysis, integration, verification, and final judgment
directly unless the user explicitly asks for delegation or there is clear
throughput/verification value.

The older multi-screen manual orchestration notes below are historical reference
only. They must not override the current workflow. In particular, do not follow
the old "always delegate implementation to Sub" rule unless the user explicitly
requests that manual multi-screen process.

---

# Legacy AGENTS.md - Multi-Screen Manual Orchestration (inactive)

> **人間（Claude）がオーケストレーターになる4画面手動運用。**
> 自動化パイプラインではなく、CCが司令塔となりSub（CX/GM/OC）に実装を委譲する。
> Detailed specs: `docs/multi-screen-sop.md`, `ai-os/knowledge/frameworks/manual_orchestration.md`

---

## Screen Configuration

| Screen | Tool | Default Model | Role | Cost |
|--------|------|---------------|------|------|
| **Main (CC)** | Claude Code | `claude-sonnet-4.6` | 司令塔・設計・統合・判断 | $20/mo |
| **Sub1 (CX)** | Codex | `gpt-5.4` | 重い実装・セキュリティレビュー | $20/mo |
| **Sub2 (GM)** | Gemini | `gemini-2.5-pro` | 調査・分析・長文脈（無制限に近い） | $20/mo |
| **Sub3 (OC)** | OpenCode Go | `opencode-go/glm-5.1` | 軽量実装・並列生成・フォールバック | $10/mo |

---

## Operation Principles

1. **CCは司令塔**。実装は絶対にSubに任せる。
2. **プロンプトはCCが作る**。人間はコピペするだけ（改変禁止）。
3. **結果の統合はCCがやる**。人間は最終判断だけ。
4. **無制限モデル（GM, OC）を優先**。コストを常に意識。
5. **記録は怠らない**。次のタスクの改善材料になる。

---

## Task Assignment Matrix

| Task Type | Primary | Review | Fallback |
|-----------|---------|--------|----------|
| 軽量スニペット | OC | — | — |
| 標準実装（M） | OC or CX | GM | OC |
| 重要実装（L） | CX | CX or GM | OC |
| 戦略設計（XL） | CC(Opus) | CX | GM |
| 調査・リサーチ | GM | CC | — |
| セキュリティレビュー | CX | CC | GM |
| リファクタ | CC(plan) + CX(impl) | GM | OC |
| 並列生成 | OC×N | CC | — |

---

## Standard Operating Procedure

See `docs/multi-screen-sop.md` for detailed steps.

### Quick Flow

```
1. CCにタスク分解を依頼 → Sub向けプロンプト生成
2. 各Subにプロンプトをコピペ
3. Sub並列実行
4. CCに結果統合を依頼
5. 人間が最終確認
```

---

## Commands

| Command | Purpose |
|---------|---------|
| `/codex-coder` 等 | 各モデルへ直接委譲（codex/opencode/gemini/local） |
| `/causal-check` | 因果推論タスクの識別戦略・推定・診断・感度分析をレビュー |
| `/verify` | 過去の実行結果を再レビュー |
| `/cleanup` | 古い成果物のGC + state.dbサイズ確認 |
| `/feedback` | 各モデルの品質フィードバックを記録 |

---

## Prompt Templates

See `ai-os/templates/prompt-templates.md` for copy-paste ready templates.

Templates for:
- Coding Task (Standard)
- Research Task
- Design Task (Critical)
- Review Task
- Refactor Task

---

## Knowledge Base

| Topic | Path |
|-------|------|
| Manual Orchestration Framework | `ai-os/knowledge/frameworks/manual_orchestration.md` |
| Multi-Screen SOP | `docs/multi-screen-sop.md` |
| Model Routing (legacy) | `ai-os/knowledge/frameworks/model_routing.md` |
| Cost Optimization | `ai-os/knowledge/frameworks/cost_optimization_patterns.md` |
| Feedback Loop | `ai-os/shared/standards/feedback_loop.md` |
| Business Frameworks | `ai-os/knowledge/business_frameworks/` |
| Causal Inference Workflow | `.claude/skills/causal-inference/SKILL.md` |

---

## Session Continuity

| File | Purpose |
|------|---------|
| `SESSION_NOTES.md` | セッション決定事項 |
| `docs/progress.md` | 進捗ログ |
| `docs/feature_list.json` | 機械可読フィーチャー状態 |
| `ai-os/shared/standards/agent_feedback.csv` | フィードバックログ |

---

## Quick Reference

```bash
# 4画面構成（tmux例）
tmux new-session -s multi-model -n main
tmux split-window -h
tmux split-window -v
tmux select-pane -t 0
tmux split-window -v

# Sub投入例
# CX: codex exec -m gpt-5.4 -s workspace-write "[prompt]"
# GM: gemini -m gemini-2.5-pro -p "[prompt]" --yolo
# OC: opencode run --model opencode-go/glm-5.1 "[prompt]"

# 直接委譲
/opencode-coder "Implement user authentication"

# フィードバック記録
/feedback --model codex --task implementation --quality 4
```
