# AI 活用ワークフロー仕様書 (2026年版)

## 目的
AI 生成能力のボトルネック（検証・スケール・再現・知識化・責任）を解決し、AI を安全かつ効率的に運用する。

## 核心原則
1. **検証ファースト**: 生成より検証を優先
2. **自動化最大化**: 人間は重点検証のみ
3. **再現性担保**: 同じ入力で同じ出力
4. **知識化**: 成功パターンを再利用
5. **責任明確化**: 最終判断は人間

---

## ツールスタック

### 検証自動化
| カテゴリ | ツール | 用途 |
|---------|--------|------|
| 静的解析 | ruff, ESLint | コード品質チェック |
| 型チェック | mypy, tsc | 型安全性 |
| セキュリティ | Semgrep, gitleaks | 脆弱性・秘密鍵検出 |
| テスト | pytest, Hypothesis | ユニット・プロパティベーステスト |
| AI レビュー | Qodo Merge, PR-Agent | 自動 PR レビュー |

### 再現性
| カテゴリ | ツール | 用途 |
|---------|--------|------|
| 依存管理 | uv, Poetry | 環境固定 |
| データバージョン | DVC | データ追跡 |
| 実験追跡 | MLflow | パラメータ・メトリクス |

### 品質メトリクス
| カテゴリ | ツール | 用途 |
|---------|--------|------|
| コードメトリクス | Radon, Pylint | 複雑度・保守性 |
| カバレッジ | pytest-cov | テスト網羅率 |
| プロンプト評価 | Promptfoo, Ragas | AI 出力品質 |

---

## 検証パイプライン

```
AI 生成コード
    │
    ▼
Stage 1: 即時検証 (< 30 秒)
├─ linter (ruff/eslint)
├─ formatter (black/prettier)
└─ type checker (mypy/tsc)
    │ (PASS のみ次へ)
    ▼
Stage 2: テスト検証 (< 2 分)
├─ unit tests (pytest)
├─ integration tests
└─ property-based (Hypothesis)
    │ (PASS のみ次へ)
    ▼
Stage 3: セキュリティ検証 (< 1 分)
├─ Semgrep rules
├─ CodeQL queries
└─ secret scanning (gitleaks)
    │ (PASS のみ次へ)
    ▼
Stage 4: AI レビュー (< 1 分)
├─ Qodo Merge review
├─ PR-Agent comments
└─ custom LLM eval (Promptfoo)
    │
    ▼
Stage 5: 人間レビュー (重点箇所のみ)
├─ ビジネスロジック
├─ アーキテクチャ決定
└─ エッジケース検証
    │
    ▼
マージ → デプロイ → 監視
```

---

## ワークフロー

### フェーズ 1: タスク分解（人間）
- `ai-os/templates/task_spec_template.md` を使用
- 受け入れ基準、制約、テスト要件を定義
- レビュー重点箇所を明示

### フェーズ 2: AI 生成 + 即時検証
- AI にタスク仕様を渡して生成
- pre-commit フックで即時検証
- テスト生成・実行

### フェーズ 3: CI パイプライン
- `.github/workflows/ai-verify.yml` で自動検証
- 全ステージ通過のみマージ可能

### フェーズ 4: 人間レビュー
- 自動検証済み項目はスキップ
- ビジネスロジック、設計判断、エッジケースに集中
- `ai-os/templates/review_checklist_template.md` を使用

### フェーズ 5: 知識化
- 成功パターンを `ai-os/knowledge/ai_patterns/` に記録
- `ai-os/templates/pattern_template.md` を使用
- 次回以降のプロンプトに反映

---

## 成功メトリクス

| メトリクス | 目標 | 測定方法 |
|-----------|------|---------|
| リードタイム | 50% 削減 | PR マージまでの時間 |
| バグ混入率 | 30% 削減 | 本番バグ数/機能数 |
| レビュー時間 | 60% 削減 | PR レビュー時間 |
| カバレッジ | 90% 以上 | カバレッジレポート |
| パターン再利用 | 月 5 件以上 | パターン集追加数 |

---

## 参照
- タスク仕様テンプレート: `ai-os/templates/task_spec_template.md`
- レビューチェックリスト: `ai-os/templates/review_checklist_template.md`
- パターンテンプレート: `ai-os/templates/pattern_template.md`
- CI パイプライン: `.github/workflows/ai-verify.yml`
- パターン集: `ai-os/knowledge/ai_patterns/`
