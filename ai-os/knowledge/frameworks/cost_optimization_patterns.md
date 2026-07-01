---
title: "Cost Optimization Patterns"
type: framework
domain: cost-management
tags: [cost, token-optimization, model-routing, budget, rtk]
created: 2026-05-05
source: "2026 best practices synthesis + rtk_guidelines.md extension"
---

## Summary
AI システムのコスト最適化フレームワーク。トークン使用量監視、モデル選択の動的切り替え、コスト/品質トレードオフ分析、予算アラート設計を体系化する。
既存 `rtk_guidelines.md` と `model_routing.md` を拡張・統合する。

## Core Principles
- **Cost-Aware Routing**: タスク難易度に応じた最適なモデル選択
- **Token Efficiency**: 不要なトークン消費を排除
- **Budget Control**: 予算閾値の監視とアラート
- **ROI Optimization**: コスト対効果の最大化
- **Transparency**: コストの可視化と追跡

## Decision Rules
- **適用条件**: 月間 AI コストが $10 を超える場合、複数モデルを使用する場合、予算制約がある場合
- **非適用条件**: 小規模実験、予算制約なしの探索的タスク

## Cost Monitoring Architecture

### トークン使用量監視
```yaml
token_monitoring:
  metrics:
    - input_tokens: count/hour
    - output_tokens: count/hour
    - total_tokens: count/hour
    - cost_usd: sum/hour
  
  aggregation:
    - hourly: true
    - daily: true
    - weekly: true
    - monthly: true
  
  attribution:
    - by_model: true
    - by_task: true
    - by_user: true
    - by_project: true
```

### リアルタイムダッシュボード
```python
class CostDashboard:
    def __init__(self):
        self.metrics = {
            "current_hour": {"tokens": 0, "cost": 0.0},
            "today": {"tokens": 0, "cost": 0.0},
            "this_week": {"tokens": 0, "cost": 0.0},
            "this_month": {"tokens": 0, "cost": 0.0}
        }
    
    def update(self, model: str, input_tokens: int, output_tokens: int):
        """メトリクスを更新"""
        cost = self.calculate_cost(model, input_tokens, output_tokens)
        
        for period in self.metrics:
            self.metrics[period]["tokens"] += input_tokens + output_tokens
            self.metrics[period]["cost"] += cost
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """コスト計算"""
        pricing = {
            "claude-sonnet-4": {"input": 3.0, "output": 15.0},  # $/1M tokens
            "gpt-4o": {"input": 2.5, "output": 10.0},
            "gemini-pro": {"input": 0.5, "output": 1.5},
            "local-llm": {"input": 0.0, "output": 0.0}
        }
        
        rates = pricing.get(model, {"input": 0.0, "output": 0.0})
        input_cost = (input_tokens / 1_000_000) * rates["input"]
        output_cost = (output_tokens / 1_000_000) * rates["output"]
        return input_cost + output_cost
    
    def check_budget(self, budget: float) -> dict:
        """予算チェック"""
        monthly_cost = self.metrics["this_month"]["cost"]
        remaining = budget - monthly_cost
        usage_pct = (monthly_cost / budget) * 100 if budget > 0 else 0
        
        return {
            "remaining": remaining,
            "usage_pct": usage_pct,
            "status": "ok" if usage_pct < 80 else "warning" if usage_pct < 100 else "exceeded"
        }
```

## Dynamic Model Routing

### 難易度ベースモデル選択
```yaml
difficulty_based_routing:
  difficulty_levels:
    XS:
      description: "1関数・1クエリ・docstring"
      models: ["local-llm"]
      cost_threshold: "$0"
    
    S:
      description: "1ファイル・明確な仕様"
      models: ["gemini-pro", "opencode-go"]
      cost_threshold: "< $0.01"
    
    M:
      description: "複数ファイル・要テスト"
      models: ["opencode-go", "gpt-4o"]
      cost_threshold: "< $0.10"
    
    L:
      description: "設計判断あり・リーク可能性あり"
      models: ["claude-sonnet-4", "gpt-4o"]
      cost_threshold: "< $1.00"
    
    XL:
      description: "アーキテクチャ変更・横断影響"
      models: ["claude-sonnet-4"]
      cost_threshold: "no limit"
  
  auto_switching:
    enabled: true
    fallback_on_error: true
    max_retries: 2
```

### 動的切り替えロジック
```python
class DynamicRouter:
    def __init__(self, budget_remaining: float):
        self.budget_remaining = budget_remaining
        self.task_history = []
    
    def select_model(self, task: dict) -> str:
        """タスクに基づいてモデルを選択"""
        difficulty = self.estimate_difficulty(task)
        
        # 予算が少ない場合は低コストモデルを優先
        if self.budget_remaining < 10:  # $10 以下
            return "local-llm" if difficulty in ["XS", "S"] else "gemini-pro"
        
        # 通常ルーティング
        routing_table = {
            "XS": "local-llm",
            "S": "opencode-go",
            "M": "opencode-go",
            "L": "claude-sonnet-4",
            "XL": "claude-sonnet-4"
        }
        
        return routing_table.get(difficulty, "opencode-go")
    
    def estimate_difficulty(self, task: dict) -> str:
        """タスク難易度を推定"""
        score = 0
        
        # ファイル数
        score += task.get("file_count", 1) * 2
        
        # 複雑度
        if task.get("requires_design", False):
            score += 10
        if task.get("requires_testing", False):
            score += 5
        if task.get("cross_cutting", False):
            score += 15
        
        # 閾値ベースで分類
        if score < 5:
            return "XS"
        elif score < 15:
            return "S"
        elif score < 30:
            return "M"
        elif score < 50:
            return "L"
        else:
            return "XL"
```

## Cost/Quality Tradeoff Analysis

### ROI 計算
```yaml
roi_analysis:
  metrics:
    - cost_per_task: float
    - quality_score: 0.0-1.0
    - time_saved: hours
    - error_rate: 0.0-1.0
  
  calculation:
    roi = (quality_score * time_saved * hourly_rate) / cost_per_task
  
  thresholds:
    high_roi: "> 10"  # 投資効果大
    medium_roi: "1-10"  # 投資効果中
    low_roi: "< 1"  # 投資効果小
```

### トレードオフマトリクス
```yaml
tradeoff_matrix:
  model: "claude-sonnet-4"
  cost_per_task: "$0.50"
  quality_score: 0.95
  time_saved: 2.0h
  hourly_rate: "$50"
  roi: 190  # (0.95 * 2.0 * 50) / 0.50
  
  model: "opencode-go"
  cost_per_task: "$0.05"
  quality_score: 0.85
  time_saved: 1.5h
  hourly_rate: "$50"
  roi: 1275  # (0.85 * 1.5 * 50) / 0.05
  
  model: "local-llm"
  cost_per_task: "$0.00"
  quality_score: 0.70
  time_saved: 1.0h
  hourly_rate: "$50"
  roi: "∞"  # コストゼロ
```

## Budget Alert Design

### 予算階層
```yaml
budget_tiers:
  daily:
    limit: "$5"
    warning_threshold: 80%  # $4
    alert_channels: ["email", "slack"]
  
  weekly:
    limit: "$25"
    warning_threshold: 80%  # $20
    alert_channels: ["email", "slack"]
  
  monthly:
    limit: "$100"
    warning_threshold: 80%  # $80
    alert_channels: ["email", "slack", "sms"]
```

### アラートルール
```yaml
alert_rules:
  - name: "daily_budget_warning"
    condition: "daily_cost > daily_limit * 0.8"
    action: "send_notification"
    severity: "warning"
  
  - name: "daily_budget_exceeded"
    condition: "daily_cost > daily_limit"
    action: "throttle_requests"
    severity: "critical"
  
  - name: "monthly_budget_warning"
    condition: "monthly_cost > monthly_limit * 0.8"
    action: "send_notification"
    severity: "warning"
  
  - name: "monthly_budget_exceeded"
    condition: "monthly_cost > monthly_limit"
    action: "switch_to_free_models"
    severity: "critical"
```

## Token Optimization Techniques

### 出力圧縮（任意）
> RTK 等の出力圧縮は**任意・非必須**（既定フローに含めない。実測削減 ~0.7%、auto-rewrite フックなし）。使う場合のみ手動で。
```yaml
output_compression:  # 任意。RTK を使う場合の例（必須ではない）
  command_compression:
    - git_status: "ファイルリスト最小化"
    - test_output: "エラーのみ強調"
    - diff_output: "本質的変更のみ抽出"
  
  context_pruning:
    - max_context_length: 4096
    - relevance_threshold: 0.7
    - auto_summarize: true
  
  prompt_efficiency:
    - remove_redundancy: true
    - use_templates: true
    - cache_responses: true
```

### プロンプト最適化パターン
```markdown
## 効率的プロンプト設計

### Before（非効率）
```
Please analyze this code and tell me what you think about it. 
I want to know if there are any issues, bugs, or improvements.
Also, please check the performance and security aspects.
And maybe suggest some refactoring if needed.
```

### After（効率的）
```
Review: [file.py]
Focus: bugs, security, performance
Output: critical_issues, suggestions
Format: markdown list
```

削減効果: トークン数 60% 削減、コスト 60% 削減
```

## Anti-patterns
- コスト監視なしで AI 使用
- 高コストモデルを一律使用
- 予算アラートなし
- トークン使用量の可視化なし
- ROI 計算なし

## Eval
- [ ] 月間コストが予算内
- [ ] トークン使用量 100% 追跡
- [ ] モデル選択の ROI 計算実施
- [ ] 予算アラート設定済み
- [ ] 四半期1回コスト最適化レビュー

## Tags
cost, token-optimization, model-routing, budget, rtk, roi, dynamic-routing
