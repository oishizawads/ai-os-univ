# Parallel Agent Workflow

複数エージェントを同時に走らせることで、文脈切り替えコストなしに調査・分析・実装を並列化できる。
Claude（PM）がオーケストレーターとして機能し、各エージェントの出力を統合する。

---

## 基本パターン

### Pattern A: 調査 × 分析の並列（コンペ序盤）

```
[start]
  ├─ researcher    → 先行事例・論文調査 → strategy_candidates.md
  └─ data-analyst  → EDA・分布確認    → eda_summary.md
[sync] → experiment-planner → design.md / tasklist.md
```

**いつ使う**: コンペ参加直後、ドメイン知識と手元データの両方を同時に把握したいとき。  
**投入例**:
```
# researcher へ
「{コンペ名} の先行事例・上位解法・ベースラインを調査してください。
 出力: ai-os/competitions/{name}/.steering/research.md」

# data-analyst へ（同時に投入）
「train.csv / test.csv の分布・欠損・ターゲット分析を行い、
 仮説を3つ挙げてください。出力: .steering/eda_summary.md」
```

---

### Pattern B: 実装 × レビューの並列（業務コード）

```
[Codex] 実装（--write）
  ↓（完了通知）
  ├─ code-reviewer     → コードスタイル・バグ検出
  └─ backend-reviewer  → API設計・インフラ整合
[sync] → Claude がフィードバックを統合して Codex に差し戻し
```

**いつ使う**: Codex がまとまった実装を返してきた直後。  
**投入例**:
```
# code-reviewer へ
「ai-os/work/{project}/src/ の変更差分をレビューしてください。
 観点: 型安全性・ログ設計・テスト欠落」

# backend-reviewer へ（同時に）
「APIエンドポイント設計と依存ライブラリを確認してください。
 観点: セキュリティ・スケーラビリティ・設定外部化」
```

---

### Pattern C: 仮説検証 × PoC の並列

```
  ├─ researcher       → 理論的根拠の確認
  └─ Codex（PoC実装） → 実装スケッチ
[sync] → experiment-planner で設計統合
```

**いつ使う**: 「この手法が有効かどうか」を素早く確認したい局面。

---

### Pattern D: エラー診断の並列

```
エラー発生
  ├─ error-analyzer  → 原因仮説（最低3つ）
  └─ researcher      → 同種エラーの先行事例
[sync] → Claude が仮説を優先順位付けして修正方針を決定
```

---

## 並列化の判断基準

| 条件 | 並列化 |
|------|--------|
| 互いの出力に依存しない | ○ |
| 同じ入力ファイルを読む（書かない） | ○ |
| 一方の出力がもう一方の入力 | ×（直列） |
| ファイルへの書き込みが競合する | × |

---

## Claude（PM）の統合手順

1. 各エージェントのタスクを同一メッセージで発行（並列起動）
2. 出力ファイルのパスを事前に合意しておく（競合防止）
3. 全エージェント完了後、出力を読んで矛盾点・ギャップを特定
4. 統合判断を `DECISION_LOG.md` に記録
5. 次のタスクを Codex または次エージェントへ渡す

---

## Codex 投入の簡略記法

```bash
# フルコマンド（ai-os/CLAUDE.md 参照）
node "C:/Users/kokao/.claude/plugins/marketplaces/openai-codex/plugins/codex/scripts/codex-companion.mjs" \
  task "タスク記述..." --write

# codex:rescue スキル経由（Claude Code 上で）
/codex:rescue タスク記述...
```

---

## 失敗パターン

- **過並列**: 3つ以上のエージェントを同時起動すると出力統合コストが増大する。2つが上限の目安
- **出力先未合意**: 複数エージェントが同じファイルに書くと競合 → 事前にパスを分ける
- **途中同期なし**: エージェントが完了しても Claude が読まずに次タスクへ進むと知識が積み上がらない
