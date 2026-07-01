---
title: "AI Output Versioning"
type: framework
domain: reproducibility
tags: [versioning, reproducibility, regression, prompt-tracking, git]
created: 2026-05-05
source: "2026 best practices synthesis"
---

## Summary
AI 出力のバージョン管理フレームワーク。プロンプト変更から出力変化までを追跡し、回帰テスト・変更影響分析・再現性担保を体系化する。
Git 連携による出力差分トラッキングとメタデータ記録を標準化する。

## Core Principles
- **Full Traceability**: プロンプト→出力の完全な追跡
- **Reproducibility**: 同じ入力で同じ出力を再現可能
- **Change Impact Analysis**: 変更の影響を事前に評価
- **Regression Prevention**: 出力品質の後退を検知
- **Git Native**: バージョン管理は Git で統一

## Decision Rules
- **適用条件**: 本番環境の AI 出力、重要な意思決定に使用される出力、再現性が求められるタスク
- **非適用条件**: 一時的な実験、破棄可能なプロトタイプ出力

## Versioning Architecture

### メタデータ構造
```yaml
output_metadata:
  version: "1.0.0"  # セマンティックバージョニング
  prompt_hash: "sha256:..."  # プロンプトのハッシュ
  model: "claude-sonnet-4-20250514"
  model_version: "2025-05-14"
  timestamp: "2026-05-05T10:30:00Z"
  seed: 42  # 再現性用シード
  temperature: 0.0  # 確率性パラメータ
  input_hash: "sha256:..."  # 入力のハッシュ
  output_hash: "sha256:..."  # 出力のハッシュ
  tags: ["production", "critical"]
  parent_version: "0.9.0"  # 親バージョン
```

### ディレクトリ構造
```
ai-os/evals/
└── versioned_outputs/
    ├── prompts/          # プロンプトバージョン
    │   ├── v1.0.0.md
    │   └── v1.1.0.md
    ├── outputs/          # 出力バージョン
    │   ├── v1.0.0/
    │   │   ├── output.md
    │   │   └── metadata.yaml
    │   └── v1.1.0/
    │       ├── output.md
    │       └── metadata.yaml
    └── regression_tests/ # 回帰テスト
        ├── baseline_v1.0.0.json
        └── current_v1.1.0.json
```

## Prompt Tracking

### プロンプトハッシュ計算
```python
import hashlib
import json

def calculate_prompt_hash(prompt: str, metadata: dict) -> str:
    """プロンプトとそのメタデータのハッシュを計算"""
    content = json.dumps({
        "prompt": prompt,
        "metadata": metadata
    }, sort_keys=True)
    return f"sha256:{hashlib.sha256(content.encode()).hexdigest()}"
```

### プロンプト変更追跡
```yaml
prompt_change_log:
  - version: "1.0.0"
    date: "2026-05-01"
    change: "初期バージョン"
    author: "user"
    impact: "none"
  
  - version: "1.1.0"
    date: "2026-05-05"
    change: "制約条件追加"
    author: "user"
    impact: "output_quality_improved"
  
  - version: "1.2.0"
    date: "2026-05-10"
    change: "出力形式変更"
    author: "user"
    impact: "breaking_change"
```

## Regression Testing

### ベースライン設定
```yaml
baseline:
  version: "1.0.0"
  output_hash: "sha256:abc123..."
  quality_metrics:
    accuracy: 0.95
    completeness: 0.90
    consistency: 0.92
  test_cases:
    - input: "test_case_1.md"
      expected_output_hash: "sha256:def456..."
    - input: "test_case_2.md"
      expected_output_hash: "sha256:ghi789..."
```

### 回帰テスト実行
```python
class RegressionTester:
    def __init__(self, baseline_path: str):
        self.baseline = self.load_baseline(baseline_path)
    
    def run_regression_test(self, current_output: dict) -> dict:
        """回帰テストを実行"""
        results = {
            "passed": True,
            "differences": [],
            "quality_delta": {}
        }
        
        # 1. ハッシュ比較
        if current_output["output_hash"] != self.baseline["output_hash"]:
            results["differences"].append("output_changed")
        
        # 2. 品質メトリクス比較
        for metric in self.baseline["quality_metrics"]:
            baseline_val = self.baseline["quality_metrics"][metric]
            current_val = current_output["quality_metrics"].get(metric, 0)
            delta = current_val - baseline_val
            
            results["quality_delta"][metric] = delta
            
            # 閾値以下なら失敗
            if delta < -0.05:  # 5% 以上低下
                results["passed"] = False
                results["differences"].append(f"{metric}_degraded")
        
        return results
```

### テスト結果記録
```markdown
## 回帰テスト結果
- テスト日時: 2026-05-05
- ベースライン: v1.0.0
- 現在バージョン: v1.1.0
- 結果: PASS / FAIL
- 差異:
  - 出力ハッシュ: 変更あり
  - 品質メトリクス:
    - accuracy: 0.95 → 0.96 (+0.01)
    - completeness: 0.90 → 0.92 (+0.02)
    - consistency: 0.92 → 0.91 (-0.01)
- 判定: 許容範囲内
```

## Change Impact Analysis

### 影響分析マトリクス
```yaml
impact_matrix:
  prompt_change:
    - type: "constraint_addition"
      impact: "output_quality_improvement"
      risk: "low"
    
    - type: "format_change"
      impact: "breaking_change"
      risk: "high"
    
    - type: "example_addition"
      impact: "output_consistency_improvement"
      risk: "low"
  
  model_change:
    - type: "version_upgrade"
      impact: "potential_output_change"
      risk: "medium"
    
    - type: "model_switch"
      impact: "significant_output_change"
      risk: "high"
```

### 影響分析フロー
```
変更提案
    │
    ├─ 変更種類分類
    │   ├─ プロンプト変更
    │   ├─ モデル変更
    │   └─ パラメータ変更
    │
    ├─ 影響範囲特定
    │   ├─ 依存する出力
    │   ├─ 下流タスク
    │   └─ 本番環境
    │
    ├─ 回帰テスト実行
    │   ├─ ベースライン比較
    │   ├─ 品質メトリクス比較
    │   └─ 閾値判定
    │
    └─ 判定
        ├─ PASS → マージ
        └─ FAIL → 修正・再テスト
```

## Git Integration

### 出力差分トラッキング
```bash
# プロンプト変更のコミット
git add ai-os/evals/versioned_outputs/prompts/v1.1.0.md
git commit -m "prompt(v1.1.0): add constraint for output format

- Add max_length constraint
- Add format specification
- Impact: output consistency improved"

# 出力変更のコミット
git add ai-os/evals/versioned_outputs/outputs/v1.1.0/
git commit -m "output(v1.1.0): regenerate with updated prompt

- Prompt hash: sha256:abc123...
- Model: claude-sonnet-4-20250514
- Quality: accuracy=0.96, completeness=0.92"
```

### Git フック統合
```bash
#!/bin/bash
# .git/hooks/pre-commit
# プロンプト変更時に回帰テストを自動実行

PROMPT_CHANGED=$(git diff --cached --name-only | grep -c "prompts/")

if [ "$PROMPT_CHANGED" -gt 0 ]; then
    echo "Running regression tests..."
    python ai-os/shared/scripts/regression_test.py
    
    if [ $? -ne 0 ]; then
        echo "Regression tests failed. Commit blocked."
        exit 1
    fi
fi
```

## Reproducibility Patterns

### シード固定パターン
```yaml
reproducibility:
  seed: 42  # 固定シード
  temperature: 0.0  # 確率性最小化
  top_p: 1.0
  max_tokens: 4096
  stop_sequences: []
  
  environment:
    python_version: "3.12"
    dependencies:
      - "anthropic==0.25.0"
      - "openai==1.30.0"
```

### 再現性検証チェックリスト
- [ ] シード固定
- [ ] 温度パラメータ記録
- [ ] モデルバージョン記録
- [ ] 入力ハッシュ記録
- [ ] 出力ハッシュ記録
- [ ] 環境情報記録
- [ ] 再実行で同一出力確認

## Anti-patterns
- プロンプト変更を記録しない
- 出力のバージョニングなし
- 回帰テストなしで本番デプロイ
- シード固定なしで再現性を主張
- モデル変更の影響を評価しない
- 出力ハッシュを検証しない

## Eval
- [ ] プロンプト変更 100% 追跡
- [ ] 回帰テスト実施率 100%
- [ ] 再現性検証成功率 95% 以上
- [ ] 出力ハッシュ検証率 100%
- [ ] 月1回バージョン監査実施

## Tags
versioning, reproducibility, regression, prompt-tracking, git, change-impact
