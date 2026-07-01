# Workspace Guide

## Mission
This workspace is optimized for data science, experimentation, and analytical decision-making.

Default stance:
- prioritize reproducibility over speed
- prefer small, testable changes over broad rewrites
- separate exploration, production code, and decision records
- do not trust a single analytical path when uncertainty is high

## タスク受領時：まず軽重トリアージ（適材適所）
**全タスク共通の一拍（軽い・必須）**: どのタスクも着手前に一度 `.claude/META_MAP.md` を通す＝8層パイプライン（集める→考える→決める→動かす→検証→伝える→残す→改善＋横断:経済性/倫理法務）の**どこに居るか位置づけ**、そして「足す前に"やらない/消す"を先に考える（stop adding, start cutting）」を一拍入れる。これは手続きではなく視点固定なので軽い。

その上で重さを見て関所の深さを変える（軽いものに重い手続きは課さない）:
- **軽い/可逆/質問** → そのまま即応。上の一拍だけでよい。
- **重い/不可逆/分析/クライアント納品** → 着手前に該当層を**深掘り**＋Pre-mortem「失敗するなら理由は」（性質判断=Cynefin／不確実なら多経路＝decision-lab／AI生成の数値・引用・コードは2経路or原典で検証／納品は実証を装わない・PII混入なし）。
- 正典スキルは領域に応じてオンデマンド（`.claude/CAPABILITY_MAP.md`）。

> 注: これは"確率を上げる関所"であって遵守の保証ではない（指示は確率的にしか守られない）。確実性が要る場面はユーザーが「検証して/多経路で」と明示要求する＝人間が最終の番人。

## Role Split
- Claude Code: **既定の実行者**。計画・実装・分析・統合・最終判断まで一貫して担う（このworkspaceの主稼働）。
- 委譲は任意の選択肢（既定ではないが、いつでも使える escape hatch）。発火するのは ①ユーザーが明示的に他AIへ振った時 ②重実装の量産・並列やトークン/スループットに実利がある時:
  - OpenCode Go / Gemini（実装・リサーチ）／ Codex（⚠️節約・実案件レビュー）
- decision-lab: 不確実性の高いデータサイエンス判断での多経路分析。

## Workspace Map
- `ai-os/`
  Main work area for company work, competitions, knowledge pipeline, and research operations.
- `decision-lab/`
  Agentic data science framework for decision-packs, parallel analysis, and convergence checks.
- `tools/`
  Local helper scripts for Codex and Gemini integrations.
- `.claude/commands/`
  Reusable Claude Code slash-command instructions.
- `.claude/skills/`
  Local skill definitions for repeated workflows.

## Default Operating Rules
- `rtk` (Rust Token Killer) is **optional and NOT part of the default flow** (deprecated as a mandatory layer 2026-06-18). Measured savings on this workload were ~0.7% (`rtk gain`, 58 cmds) — the real token sinks here are MCP/graph context and file reads, not CLI stdout. No auto-rewrite hook is installed; `rtk` is not on PATH.
  - Ad-hoc manual use only: `C:/workspace/bin/rtk.exe <command>` (e.g. `rtk.exe gain`).
  - Details: `ai-os/shared/standards/rtk_guidelines.md`.
- For coding tasks, read the nearest local context files first.
- For data science tasks, identify:
  - objective
  - target
  - validation strategy
  - leakage risks
  - output artifact path
- Keep exploratory code separate from production code.
- Record decisions that affect experiment interpretation.
- Do not accept model output without checking it against the codebase, data assumptions, and metrics.

## Data Science Workflow
Use this default sequence unless the project already defines another one:
1. Read `CLAUDE.md`, project notes, and `SESSION_NOTES.md`.
2. Clarify objective, constraints, and success criteria.
3. Establish or verify a baseline.
4. Make the smallest change that tests one hypothesis.
5. Validate before optimizing.
6. Record findings and next hypotheses.

## Artifact Conventions
- exploratory work: notebooks, scratch analysis, prototype scripts
- production work: stable code under `src/` or project-defined production paths
- records: `SESSION_NOTES.md`, `result.md`, `.steering/`, decision logs

When unsure:
- keep analysis artifacts easy to diff
- prefer markdown records over memory-only decisions
- make filenames descriptive and date-aware when logging outputs

## Model Routing — トークンコスト最適化

**原則: Claude直接が既定（設計も実行も担う）。委譲は ①ユーザーが明示指定した時 ②token/スループットに実利がある時のオプションで、必須ではない（いつでも使える）。**  
**Codex は利用制限あり。実案件レビュー・重要度高タスクのみに温存する。**

| タスク | 優先モデル | 予備 | コマンド |
|--------|-----------|------|---------|
| 設計・判断・レビュー・合成 | **Claude** | — | — (自分) |
| 実装全般（デフォルト） | **Claude直接** | OpenCode/Gemini（委譲時のみ） | `/opencode-coder` |
| Webリサーチ・ドキュメント調査 | **Gemini** | — | `/gemini-coder` |
| 実案件コードレビュー・重要実装 | **Codex** ⚠️要節約 | OpenCode | `/codex:rescue` |
| 金融・不確実性分析 | **decision-lab** | — | `decision-lab/` 参照 |

### Codex 使用条件（⚠️ 制限あり・要節約）
以下のいずれかに該当する場合のみ使用:
- 実案件（クライアント向け）のコードレビュー
- 本番影響あり・セキュリティ関連の実装
- OpenCode / Gemini の結果が明らかに不十分だった場合のフォールバック

詳細な決定木: `ai-os/knowledge/frameworks/model_routing.md`  

### 利用可能なモデル（2026-06-19 時点・制限値は変動するため要再確認）

| エージェント | 実際のモデル | 制限 |
|------------|-------------|------|
| Claude Code | **Opus 4.8** | 時点で変動・要確認 |
| OpenCode Go | qwen3.6-plus (opencode-go) | なし |
| Gemini | gemini-2.5-flash / gemini-3 | 日次 Flash 2%、Pro 0% |
| Codex | gpt-5.4 (reasoning medium) | 週次100%残り |

## decision-lab Usage
Use `decision-lab` when the task is analytical and a single-path agent answer is not trustworthy enough.

Good fits:
- marketing mix modeling
- forecasting
- causal-ish decision support
- model comparison under uncertainty
- analyses where robustness matters more than a quick answer

Not the first choice for:
- simple app coding
- one-off utility scripts
- small bug fixes

Suggested adoption order:
1. inspect `decision-lab/README.md`
2. inspect `decision-lab/docs/decision-packs.md`
3. inspect `decision-lab/docs/parallel-agents.md`
4. start from an existing decision-pack before creating a new one

## Practical Defaults For This Workspace
- If the task is mostly implementation: Claude does it directly. Delegate only when the user asks, or for bulk/parallel work or real token/throughput pressure.
- If the task is mostly analysis under uncertainty: consider `decision-lab`.
- If the task touches experiments: preserve validation integrity and write down what changed.

## Session Start Checklist
Before substantial work:
- identify the target project directory
- read local notes and constraints
- identify whether the task is coding, analysis, or both
- decide whether it needs a baseline, a second coding opinion, or a decision-pack workflow

## 補足リファレンス
運用の詳細は `.claude/REFERENCE.md` に集約（常時はロードせず必要時に参照）:
- AI委譲は直接コマンド（`/opencode-coder` 等）のみ。`/route`・`/orchestrate`系・ai-delegate は廃止（2026-06-19）
- AI活用ベストプラクティス（セキュリティ・協調・出力管理・コスト最適化のフレームワーク群）
- AI活用ワークフロー仕様（検証・テンプレート・CI）
- フィードバックループ `/feedback` ／ NotebookLM連携 `/notebooklm-export` ／ Helper Functions

モデルルーティングの決定木: `ai-os/knowledge/frameworks/model_routing.md`

<!-- gitnexus:start -->
