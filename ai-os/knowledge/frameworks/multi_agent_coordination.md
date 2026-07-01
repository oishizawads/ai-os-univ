---
title: "Multi-Agent Coordination Patterns"
type: framework
domain: agentic-workflow
tags: [multi-agent, coordination, deadlock, goal-drift, self-healing, ankh]
created: 2026-05-05
source: "2026 best practices synthesis + ankh_swarm_protocol.md extension"
---

## Summary
マルチエージェントシステムにおける協調パターン。デッドロック検出・回復、目標逸脱防止、自己修復、エージェント間契約設計を体系化。
既存 `ankh_swarm_protocol.md` の MAP スキーマと統合し、実用的な協調ワークフローを提供する。

## Core Principles
- **Explicit Contracts**: エージェント間は明確な入出力契約で連携
- **Fail-Fast**: 異常は早期検知・早期回復
- **Goal Alignment**: 全エージェントの目標は上位目標と整合
- **Observability**: 全エージェントの状態は監視可能
- **Graceful Degradation**: 一部障害でも全体は機能継続

## Decision Rules
- **適用条件**: 3つ以上のエージェントが協調する場合、長時間実行タスク、クリティカルな意思決定
- **非適用条件**: 単一エージェントで完結するタスク、単純な直列処理

## Coordination Patterns

### 1. デッドロック検出・回復

#### 検出メカニズム
```yaml
deadlock_detection:
  - timeout: 30s  # 応答タイムアウト
  - cycle_detection: true  # 循環依存検出
  - resource_wait_limit: 3  # リソース待機上限
  - heartbeat_interval: 5s  # ハートビート間隔
```

#### 回復パターン
```
デッドロック検知
    │
    ├─ タイムアウト → タスク再割り当て
    ├─ 循環依存 → 優先度ベースで一方を中断
    ├─ リソース競合 → キューイングまたは代替リソース
    └─ ハートビート喪失 → エージェント再起動・フォールバック
```

#### 実装テンプレート
```python
class DeadlockDetector:
    def __init__(self, timeout=30, heartbeat_interval=5):
        self.timeout = timeout
        self.heartbeat_interval = heartbeat_interval
        self.waiting_graph = {}  # エージェント間の待機関係
    
    def detect_cycle(self) -> bool:
        """循環依存を検出"""
        visited = set()
        path = set()
        for agent in self.waiting_graph:
            if self._has_cycle(agent, visited, path):
                return True
        return False
    
    def _has_cycle(self, agent, visited, path) -> bool:
        visited.add(agent)
        path.add(agent)
        for dependent in self.waiting_graph.get(agent, []):
            if dependent not in visited:
                if self._has_cycle(dependent, visited, path):
                    return True
            elif dependent in path:
                return True
        path.remove(agent)
        return False
    
    def resolve(self) -> str:
        """デッドロックを解消"""
        if self.detect_cycle():
            # 優先度最低のエージェントを中断
            lowest_priority = min(
                self.waiting_graph.keys(),
                key=lambda a: self.get_priority(a)
            )
            return f"interrupt:{lowest_priority}"
        return "no_deadlock"
```

### 2. 目標逸脱（Goal Drift）防止

#### 検証チェックポイント
```yaml
goal_validation:
  - checkpoint_interval: 5  # タスク5回ごとに検証
  - alignment_threshold: 0.8  # 目標整合性閾値
  - drift_detection: true  # 逸脱検出
  - correction_mechanism: "realign"  # 修正メカニズム
```

#### 検証フロー
```
タスク実行
    │
    ├─ チェックポイント到達
    │   │
    │   ├─ 現在状態と目標の整合性計算
    │   ├─ 閾値以下 → 警告・修正
    │   └─ 閾値以上 → 続行
    │
    └─ 逸脱検知時
        ├─ 原因分析（プロンプト？コンテキスト？）
        ├─ 目標再提示
        └─ 必要に応じてエスカレーション
```

#### 整合性計算
```python
def calculate_goal_alignment(current_state, goal_spec) -> float:
    """現在状態と目標の整合性を計算"""
    # 1. タスク完了度
    completion = calculate_completion_rate(current_state, goal_spec)
    
    # 2. 品質基準適合度
    quality = calculate_quality_score(current_state, goal_spec)
    
    # 3. 制条件遵守度
    constraints = calculate_constraint_compliance(current_state, goal_spec)
    
    # 加重平均
    alignment = 0.4 * completion + 0.4 * quality + 0.2 * constraints
    return alignment
```

### 3. 自己修復パターン

#### 異常検知→回復フロー
```
異常検知
    │
    ├─ 種類分類
    │   ├─ 一時的エラー → 再試行（指数バックオフ）
    │   ├─ 設定エラー → 設定リロード
    │   ├─ リソース不足 → スケールアップ/代替リソース
    │   └─ 論理エラー → フォールバックエージェント
    │
    └─ 回復確認
        ├─ 成功 → 続行・ログ記録
        └─ 失敗 → エスカレーション・手動介入
```

#### 再試行パターン
```yaml
retry_policy:
  - max_retries: 3
  - backoff_multiplier: 2  # 指数バックオフ
  - initial_delay: 1s
  - max_delay: 30s
  - jitter: true  # ジッター追加（集中回避）
```

### 4. エージェント間契約設計

#### 契約仕様
```yaml
agent_contract:
  input:
    format: "JSONC"  # MAP スキーマ準拠
    required_fields: ["task_id", "input_data", "constraints"]
    validation: "JSON Schema"
  
  output:
    format: "JSONC"
    required_fields: ["task_id", "result", "status", "metadata"]
    validation: "JSON Schema"
  
  error_handling:
    format: "JSONC"
    required_fields: ["task_id", "error_code", "error_message", "recovery_suggestion"]
  
  sla:
    response_time: 30s
    availability: 99.9%
    max_error_rate: 1%
```

#### MAP スキーマ統合
```jsonc
// .agent/agent.jsonc - エージェント契約定義
{
  "agent_id": "data-analyst-01",
  "persona": "データ分析専門家",
  "capabilities": ["eda", "visualization", "hypothesis_generation"],
  "input_contract": {
    "schema": "map://input/v1",
    "required": ["dataset_path", "analysis_objective"]
  },
  "output_contract": {
    "schema": "map://output/v1",
    "required": ["findings", "visualizations", "next_steps"]
  },
  "sla": {
    "timeout": 120,
    "max_retries": 2
  }
}
```

## Coordination Topologies

### 1. 中央集権型（Orchestrator）
```
    Orchestrator
    /    |    \
Agent1 Agent2 Agent3
```
- **利点**: 制御が容易、目標整合性が高い
- **欠点**: Orchestrator がボトルネック、単一障害点
- **適用**: 明確な上下関係があるタスク

### 2. 分散型（Peer-to-Peer）
```
Agent1 ↔ Agent2 ↔ Agent3
```
- **利点**: 耐障害性、スケーラビリティ
- **欠点**: 調整が複雑、目標逸脱リスク
- **適用**: 同等の専門性が必要なタスク

### 3. ハイブリッド型
```
    Orchestrator
    /           \
Sub-Orch1     Sub-Orch2
 /    \        /    \
A1    A2      A3    A4
```
- **利点**: スケールと制御のバランス
- **欠点**: 設計が複雑
- **適用**: 大規模・階層的タスク

## Anti-patterns
- 契約 없이 エージェント間連携
- デッドロック検出なしの並列実行
- 目標検証チェックポイントなし
- 自己修復メカニズムなし
- 単一障害点の放置
- ハートビート監視なし

## Eval
- [ ] デッドロック検出率 100%
- [ ] 目標逸脱検知率 95% 以上
- [ ] 自己修復成功率 90% 以上
- [ ] エージェント間契約違反 0 件
- [ ] 月1回協調テスト実施

## Tags
multi-agent, coordination, deadlock, goal-drift, self-healing, ankh, map, swarm
