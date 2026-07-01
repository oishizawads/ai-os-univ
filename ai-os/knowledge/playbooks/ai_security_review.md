---
title: "AI Security Review Playbook"
type: playbook
domain: security
tags: [security, review, checklist, automation, compliance]
created: 2026-05-05
source: "2026 best practices synthesis"
---

## Summary
AI システムのセキュリティレビュー手順。開発前・開発中・リリース前の各段階で実施するチェック項目と自動化ルールを定義する。
`ai_security_guardrails.md` と連携し、実用的なレビューワークフローを提供する。

## Core Principles
- **Shift Left**: セキュリティは早期に組み込む
- **Automate First**: 可能な限り自動チェック
- **Human Focus**: 人間は高次の判断に集中
- **Continuous**: 継続的なレビューと改善
- **Document**: すべてのレビューを記録

## Review Stages

### Stage 1: 開発前レビュー

#### チェックリスト
- [ ] セキュリティ要件定義
- [ ] リスクアセスメント実施
- [ ] 脅威モデル作成
- [ ] コンプライアンス要件特定
- [ ] セキュリティテスト計画策定

#### 自動化項目
```yaml
pre_dev_automation:
  - threat_model_generator: true
  - compliance_checker: true
  - risk_assessment_template: true
```

#### 出力物
- セキュリティ要件書
- リスクアセスメント報告書
- 脅威モデル図
- テスト計画書

### Stage 2: 開発中レビュー

#### チェックリスト
- [ ] 入力バリデーション実装確認
- [ ] プロンプトインジェクションテスト
- [ ] データマスキング確認
- [ ] エラーハンドリング見直し
- [ ] 依存パッケージ脆弱性スキャン

#### 自動化項目
```yaml
dev_automation:
  - input_validation_tester: true
  - prompt_injection_scanner: true
  - data_masking_verifier: true
  - dependency_scanner: true
  - static_analysis: true
```

#### 自動化スクリプト
```bash
#!/bin/bash
# 開発中セキュリティチェック

echo "=== Input Validation Test ==="
python ai-os/shared/scripts/test_input_validation.py

echo "=== Prompt Injection Scan ==="
python ai-os/shared/scripts/scan_prompt_injection.py

echo "=== Data Masking Check ==="
python ai-os/shared/scripts/check_data_masking.py

echo "=== Dependency Scan ==="
uv run safety check

echo "=== Static Analysis ==="
uv run semgrep --config auto src/
```

#### 出力物
- セキュリティテスト結果
- 脆弱性スキャン報告書
- 修正項目リスト

### Stage 3: リリース前レビュー

#### チェックリスト
- [ ] セキュリティレビュー実施（本チェックリスト）
- [ ] プロンプトインジェクション耐性確認
- [ ] 出力フィルタリング動作確認
- [ ] 監査ログ記録確認
- [ ] インシデント対応計画確認
- [ ] コンプライアンス適合確認
- [ ] パフォーマンステスト（セキュリティ影響）
- [ ] バックアップ・復旧手順確認

#### 自動化項目
```yaml
pre_release_automation:
  - full_security_scan: true
  - compliance_report_generator: true
  - audit_log_verifier: true
  - incident_response_tester: true
```

#### レビューフロー
```
開発完了
    │
    ├─ 自動セキュリティスキャン
    │   ├─ プロンプトインジェクションテスト
    │   ├─ データ流出テスト
    │   ├─ 出力フィルタリングテスト
    │   └─ 依存パッケージスキャン
    │
    ├─ 人間レビュー
    │   ├─ 脅威モデル見直し
    │   ├─ リスクアセスメント更新
    │   ├─ コンプライアンス確認
    │   └─ インシデント対応計画確認
    │
    └─ 判定
        ├─ PASS → リリース
        └─ FAIL → 修正・再テスト
```

#### 出力物
- セキュリティレビュー報告書
- コンプライアンス適合証明書
- リリース承認書

## Automated Check Rules

### ルール定義
```yaml
security_rules:
  - id: "SEC001"
    name: "input_validation"
    description: "入力バリデーションが実装されている"
    severity: "critical"
    auto_check: true
  
  - id: "SEC002"
    name: "prompt_injection_resistance"
    description: "プロンプトインジェクションに耐性がある"
    severity: "critical"
    auto_check: true
  
  - id: "SEC003"
    name: "data_masking"
    description: "機密データがマスキングされている"
    severity: "high"
    auto_check: true
  
  - id: "SEC004"
    name: "output_filtering"
    description: "出力フィルタリングが機能している"
    severity: "high"
    auto_check: true
  
  - id: "SEC005"
    name: "audit_logging"
    description: "監査ログが記録されている"
    severity: "medium"
    auto_check: true
  
  - id: "SEC006"
    name: "dependency_security"
    description: "依存パッケージに脆弱性がない"
    severity: "high"
    auto_check: true
```

### 自動チェック結果フォーマット
```json
{
  "rule_id": "SEC001",
  "status": "pass",
  "details": "Input validation implemented with allowlist patterns",
  "timestamp": "2026-05-05T10:30:00Z",
  "evidence": "src/validators/input.py:42"
}
```

## Human Review Focus Areas

### 高次判断項目
1. **脅威モデルの妥当性**
   - 新規脅威の特定
   - リスク評価の適切性
   - 緩和策の有効性

2. **コンプライアンス適合**
   - 規制要件の網羅性
   - 証拠の十分性
   - 監査対応準備

3. **インシデント対応計画**
   - 対応フローの現実性
   - 役割分担の明確さ
   - 訓練計画の適切性

4. **ビジネスリスク評価**
   - セキュリティ投資のROI
   - リスク受容の判断
   - 代替案の評価

## Review Documentation

### レビュー報告書テンプレート
```markdown
# AI セキュリティレビュー報告書

## 基本情報
- レビュー日時: YYYY-MM-DD
- レビュアー: 名前・役割
- 対象システム: システム名・バージョン
- レビュー段階: 開発前 / 開発中 / リリース前

## 自動チェック結果
| ルールID | 項目 | 結果 | 備考 |
|---------|------|------|------|
| SEC001 | 入力バリデーション | PASS | |
| SEC002 | プロンプトインジェクション耐性 | PASS | |
| SEC003 | データマスキング | FAIL | 修正必要 |

## 人間レビュー結果
### 脅威モデル
- 新規脅威: なし
- リスク評価: 適切
- 緩和策: 有効

### コンプライアンス
- 規制要件: 網羅的
- 証拠: 十分
- 監査対応: 準備完了

## 総合判定
- 結果: PASS / FAIL
- 理由: 
- 修正項目: 
- 次回レビュー予定: 

## 署名
- レビュアー: 
- 承認者: 
```

## Integration with Existing Workflows

### CI/CD 統合
```yaml
# .github/workflows/security-review.yml
name: AI Security Review

on:
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 10 * * 1'  # 毎週月曜日10:00

jobs:
  security-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      
      - name: Install dependencies
        run: |
          pip install uv
          uv sync --frozen
      
      - name: Run Security Checks
        run: |
          uv run semgrep --config auto src/
          uv run safety check
          python ai-os/shared/scripts/scan_prompt_injection.py
      
      - name: Generate Report
        run: python ai-os/shared/scripts/generate_security_report.py
      
      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: security-report
          path: reports/security-*.md
```

### Git フック統合
```bash
#!/bin/bash
# .git/hooks/pre-push
# プッシュ前にセキュリティチェック

echo "Running pre-push security checks..."

# 入力バリデーションテスト
python ai-os/shared/scripts/test_input_validation.py
if [ $? -ne 0 ]; then
    echo "Input validation tests failed. Push blocked."
    exit 1
fi

# プロンプトインジェクションスキャン
python ai-os/shared/scripts/scan_prompt_injection.py
if [ $? -ne 0 ]; then
    echo "Prompt injection scan failed. Push blocked."
    exit 1
fi

echo "All security checks passed."
exit 0
```

## Anti-patterns
- セキュリティレビューを最後に実施
- 自動チェックを信頼しすぎ
- 人間レビューを省略
- レビュー結果を記録しない
- 修正項目を追跡しない
- 定期的なレビューを省略

## Eval
- [ ] 全 PR でセキュリティレビュー実施
- [ ] 自動チェック実施率 100%
- [ ] 人間レビュー実施率 100%
- [ ] 修正項目完了率 95% 以上
- [ ] 四半期1回包括的レビュー
- [ ] セキュリティインシデント 0 件

## Tags
security, review, checklist, automation, compliance, ci-cd, git-hooks
