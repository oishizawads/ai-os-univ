# Harness Engineering 導入計画書

## 目的

Aicon社の「ハーネスエンジニアリング」（[Zenn記事](https://zenn.dev/aicon_kato/articles/harness-engineering-startup)）を、ソロ開発者向けに最小コストで再現する。

最終ゴール: **GitHub Issueに要件を書く → 朝にはマージ済みPR**

## 制約と前提

- **ソロ開発者**（Claude=PM / Codex=Engineer）
- **API直接課金は不可** → Claude Code サブスク内で完結させる
- 全リポジトリで使えるテンプレ化が必須
- 実行モデルは既定の Claude Code モデル（再陳腐化を避け固定値は書かない）
- 重い要件定義・詳細設計の壁打ち時のみ手動で上位モデルへ切替

## コスト見積

| 要素 | コスト |
|------|--------|
| Claude Code Action | サブスク内 (追加$0) |
| GitHub Actions 実行時間 | 無料枠2000分/月 (private) |
| Codex CLI | ローカル実行 ($0) |
| API直接呼び出し | 使わない ($0) |

**追加コスト: $0** を維持する。

## 9段階プロセス（記事準拠 → 簡略版）

### 記事の9段階
要求 → 要件定義 → 基本設計 → 詳細設計 → 実装 → 設計分割 → サブタスク化 → featureブランチ → devマージ

### 当面の簡略版（4段階）
| 段階 | 担当 | 出力 |
|------|------|------|
| ① 要求 | 人間 | 親Issue（背景・ゴール・制約） |
| ② 要件定義 | Claude | コメントで壁打ち→確定 |
| ③ 実装 | Codex | 子Issue→PR |
| ④ レビュー | Claude | レビュー→修正指示→マージ |

P4以降で記事の9段階に拡張する。

## ラベル設計

```
status:requirement      要件定義中
status:design           設計中
status:ready            実装待ち
status:implementing     実装中
status:review           レビュー中
status:merged           完了

priority:high
priority:medium
priority:low

type:feature
type:bug
type:refactor
type:experiment

agent:claude            Claudeが担当中
agent:codex             Codexが担当中
agent:human             人間の判断待ち
```

## エージェントマッピング

記事の21体を役割で集約し、既存資産＋ECCから移植したものでカバーする。

| 記事の役割 | 担当 | 状態 |
|----------|------|------|
| 要件定義 | `experiment-planner` / `product-analyst` | 既存 |
| 詳細設計 | `planner` (ECCから追加) | 既存 |
| 実装 | Codex CLI | 既存 |
| レビュー | `code-reviewer` / `backend-reviewer` | 既存 |
| 修正 | Codex | 既存 |
| エラー解析 | `error-analyzer` | 既存 |
| 影響分析 | `code-explorer` (ECCから追加) | 既存 |
| 隠れバグ検出 | `silent-failure-hunter` (ECCから追加) | 既存 |
| クリーンアップ | `refactor-cleaner` (ECCから追加) | 既存 |
| CI修正 | (P5で追加) | 未実装 |
| 自動マージ | (P4で追加) | 未実装 |

## フェーズ計画

### P1: 型化（今日）
**目標**: 全リポジトリで使えるテンプレ・ラベル・ドキュメント整備

成果物:
- `templates/harness/ISSUE_TEMPLATE/feature_request.md`
- `templates/harness/ISSUE_TEMPLATE/implementation_task.md`
- `templates/harness/ISSUE_TEMPLATE/bug_report.md`
- `templates/harness/LABELS.md`
- `templates/harness/WORKFLOW.md`
- `templates/harness/setup-labels.sh` （`gh` でラベル一括投入）
- `templates/harness/install.sh` （任意リポジトリにテンプレ展開）

完了条件: 任意のリポジトリで `bash install.sh` 一発でラベル＋テンプレが揃う。

### P2: 半自動運用（今週）
**目標**: 手動でフローを踏みながら型を体に染み込ませる

成果物:
- `templates/harness/RUNBOOK.md` （ラベル変更→次にやることの手順書）
- 1リポジトリで実際に1サイクル回す（Issue→PR→merge）

完了条件: ラベル付与→`/codex:rescue`起動→PR→レビュー→マージの手順が手で再現できる。

### P3: GitHub Actions導入（来週）
**目標**: 1リポジトリで Claude Code Action を稼働させる

成果物:
- `templates/harness/.github/workflows/claude-on-mention.yml`
  （Issueで `@claude` → Claudeが自動応答）
- `templates/harness/.github/workflows/claude-on-label.yml`
  （`status:requirement` ラベル付与 → Claude が要件壁打ち開始）

完了条件: Issueにメンション or ラベル付与でClaudeが自動でコメント返す。

### P4: バトンリレー（数週間）
**目標**: ラベル→Action→次ラベル付与→次Action のチェーン

成果物:
- `claude-on-label.yml` を拡張し、要件確定→`status:design`自動遷移
- `codex-on-label.yml` (ローカルRunner経由 or Codex GitHub App)
- 設計完了→実装Issue自動分割するロジック

完了条件: 親Issueに要求書く→人間は壁打ち応答だけ→子Issue自動生成→実装PR自動作成。

### P5: CI統合・完全パイプライン（1ヶ月後）
**目標**: テスト・lint・型チェック失敗を自動修正

成果物:
- CI失敗→Codex自動修正のフロー
- 影響分析自動コメント
- 自動マージ条件の定義（CI green + レビューOK）

完了条件: 単純な機能追加なら人間は要件定義のみで朝には完了している。

## モデル運用ポリシー

| 場面 | デフォルト | Opus切替条件 |
|------|----------|------------|
| 要件定義の壁打ち | 既定モデル | 業務ドメインが複雑/未知のとき手動で上位モデル |
| 詳細設計 | 既定モデル | アーキ判断が重いとき手動で上位モデル |
| 実装 | Codex (gpt-5.4) | n/a |
| レビュー | 既定モデル | 重要案件のみ上位モデル |
| エラー解析 | 既定モデル | 切り分けが詰まったとき上位モデル |

**原則: 既定モデルで動かす。詰まったら人間判断で上位モデルへ切替。**

## リスクと回避策

| リスク | 回避策 |
|-------|-------|
| GitHub Actions無料枠超過 | private repoは月2000分まで。超えそうなら public化 or self-hosted runner検討 |
| 既定モデルで設計が浅くなる | まず既定モデルで壁打ち→不足を感じたら手動で上位モデル再生成 |
| バトンリレーで暴走 | 各エージェントの実行ログをIssueコメントに残す。ラベルに `agent:human` で停止可 |
| テンプレが現場に合わない | P2で1サイクル回して感触確認、テンプレ改訂 |

## 進捗管理

このファイル自体を進捗ボードとする。各フェーズに以下を追記:
- `Started: YYYY-MM-DD`
- `Completed: YYYY-MM-DD`
- 学び・改善点

## 関連ドキュメント

- 元記事: https://zenn.dev/aicon_kato/articles/harness-engineering-startup
- ai-os 全体構成: `C:/workspace/CLAUDE.md`
- Codex連携: `C:/workspace/ai-os/CODEX.md`
- 既存agent一覧: `C:/workspace/ai-os/AGENTS.md`
