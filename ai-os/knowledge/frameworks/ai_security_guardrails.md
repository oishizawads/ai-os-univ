---
title: "AI Security Guardrails"
type: framework
domain: security
tags: [security, guardrails, prompt-injection, data-leak, compliance]
created: 2026-05-05
source: "2026 best practices synthesis"
---

## Summary
AI システムのセキュリティリスク（プロンプトインジェクション、データ流出、出力改ざん）を予防・検知・対応するためのガードレールフレームワーク。
開発・本番・レビュー各段階で自動チェックと人間検証を組み合わせ、EU AI Act および国内規制に準拠する。

## Core Principles
- **Zero Trust AI**: AI 出力を信頼せず、常に検証する
- **Defense in Depth**: 多層防御（入力→処理→出力→監視）
- **Least Privilege**: AI に必要な最小限の権限・データのみ付与
- **Auditability**: すべての AI 操作は追跡可能であること
- **Fail Secure**: 異常検知時は安全側に倒す

## Decision Rules
- **適用条件**: 本番環境に AI をデプロイする場合、機密データを扱う場合、外部公開出力を生成する場合
- **非適用条件**: ローカルのみの実験、公開データのみ使用、一時的なプロトタイプ

## Threat Model

### 1. プロンプトインジェクション
- **直接インジェクション**: ユーザー入力がプロンプトに混入
- **間接インジェクション**: 外部データ（Web、DB）に悪意あるコンテンツ
- **マルチターン攻撃**: 複数回の対話で制限を迂回

### 2. データ流出
- **トレーニングデータ漏洩**: 機密情報が出力に含まれる
- **コンテキスト漏洩**: システムプロンプトや内部情報が暴露
- **サイドチャネル**: タイミング、エラーメッセージからの推測

### 3. 出力改ざん
- **意図しない動作**: 悪意あるコード生成
- **バイアス増幅**: 差別的・有害な出力
- **事実捏造**: ハルシネーションによる誤情報

## Guardrails Design

### 入力段階ガードレール
```yaml
input_validation:
  - max_length: 4096  # 入力長制限
  - allowlist_patterns: []  # 許可パターン
  - blocklist_patterns:  # 禁止パターン
    - "ignore previous instructions"
    - "system prompt"
    - "override security"
    - "<script>"
    - "DROP TABLE"
  - sanitize: true  # HTML/JS エスケープ
  - rate_limit: 100/hour  # レートリミット
```

### 処理段階ガードレール
```yaml
processing_controls:
  - context_isolation: true  # セッション間分離
  - data_masking:  # マスキング対象
    - PII: true
    - credentials: true
    - api_keys: true
  - execution_sandbox: true  # サンドボックス実行
  - timeout: 30s  # 処理タイムアウト
```

### 出力段階ガードレール
```yaml
output_validation:
  - content_filter:  # フィルタリング
    - toxicity: true
    - pii_leak: true
    - code_execution: false  # 自動実行禁止
  - hash_verification: true  # 出力ハッシュ記録
  - signature: true  # 署名付き出力（オプション）
  - max_output_length: 8192
```

## Security Checklist

### 開発段階
- [ ] 入力バリデーション実装済み
- [ ] プロンプトインジェクションテスト実施
- [ ] 機密データマスキング確認
- [ ] サンドボックス環境でテスト
- [ ] エラーハンドリング（情報漏洩なし）

### レビュー段階
- [ ] セキュリティレビュー実施（`ai_security_review.md` 参照）
- [ ] プロンプトインジェクション耐性確認
- [ ] 出力フィルタリング動作確認
- [ ] 監査ログ記録確認
- [ ] 依存パッケージ脆弱性スキャン

### 本番段階
- [ ] レートリミット設定
- [ ] 監視アラート設定
- [ ] インシデント対応計画策定
- [ ] 定期セキュリティテスト計画
- [ ] バックアップ・復旧手順確認

## Compliance

### EU AI Act 対応
- **リスク分類**: AI システムのリスクレベルを特定
- **透明性**: AI 使用の開示
- **データガバナンス**: トレーニングデータの品質・バイアス管理
- **監視**: 継続的なパフォーマンス監視
- **インシデント報告**: 重大インシデントの報告義務

### 国内規制対応
- **個人情報保護法**: PII 処理の適法性
- **サイバーセキュリティ基本法**: セキュリティ対策
- **業界規制**: 金融、医療、公共分野の追加要件

## Monitoring & Alerting

### メトリクス
```yaml
security_metrics:
  - prompt_injection_attempts: count/hour
  - data_leak_detections: count/hour
  - output_filter_triggers: count/hour
  - rate_limit_violations: count/hour
  - anomaly_scores: 0.0-1.0
```

### アラート閾値
```yaml
alert_thresholds:
  - prompt_injection_attempts: > 10/hour → WARNING
  - data_leak_detections: > 0 → CRITICAL
  - output_filter_triggers: > 50/hour → WARNING
  - anomaly_scores: > 0.8 → CRITICAL
```

## Incident Response

### 対応フロー
1. **検知**: 自動アラートまたは人間報告
2. **隔離**: 影響範囲の特定・隔離
3. **調査**: ログ分析・原因特定
4. **修復**: パッチ適用・設定変更
5. **報告**: 関係者への報告・記録
6. **改善**: 再発防止策の実装

### 記録テンプレート
```markdown
## セキュリティインシデント記録
- 発生日時:
- 検知方法:
- 影響範囲:
- 原因:
- 対応内容:
- 再発防止策:
- 記録者:
```

## Anti-patterns
- AI 出力を盲信して検証しない
- プロンプトに機密情報を直接埋め込む
- 入力バリデーションを省略する
- 監査ログを記録しない
- インシデント対応計画がない

## Eval
- [ ] プロンプトインジェクションテストを月1回実施
- [ ] データ流出検知率 99% 以上
- [ ] セキュリティレビューを全 PR で実施
- [ ] インシデント対応訓練を四半期1回実施
- [ ] コンプライアンス監査を年1回実施

## Tags
security, guardrails, prompt-injection, data-leak, compliance, eu-ai-act, incident-response
