# Claude ↔ Codex 対話進行プロンプト

## 目的

`.claude/improvements/ideas.md` の 65個の改善アイデアについて、Claude（Advocate）と Codex（Critic）が対話し、**実装すべきアイデアを絞り込む**。

---

## 参加者

| 役割 | AI | 役割 |
|---|---|---|
| Advocate | Claude | アイデアの戦略的価値を擁護・統合 |
| Critic | Codex | 技術的・運用的・経済的リスクを批判 |

---

## 対話フロー

### Round 1：個別レビュー

1. **Claude に `claude-advocate.md` を与える**
   - 入力：`.claude/improvements/ideas.md`
   - 出力：Top 10 推奨アイデア + 統合案 + 反論メモ

2. **Codex に `codex-critic.md` を与える**
   - 入力：`.claude/improvements/ideas.md`
   - 出力：削るべき Top 10 + リスクマトリックス + 最小実装案 + 反論メモ

### Round 2：相互批判

3. **Codex の出力を Claude に渡す**
   - 「Codex はこう批判している。あなたはどう反論する？」
   - 出力：反論 + 修正された Top 10

4. **Claude の出力を Codex に渡す**
   - 「Claude はこう擁護している。あなたはどう批判する？」
   - 出力：追加批判 + 修正された削るべきリスト

### Round 3：収束

5. **両方の出力を人間が確認**
   - 一致した部分（両方が Low Risk / High Return と評価）を採用候補に
   - 食い違った部分は人間が最終判断

6. **Claude に最終統合を依頼**
   - 「議論を踏まえて、最初に導入すべき3つを提案」
   - 出力：最終推奨3つ + 実装順序 + 測定指標

---

## 評価シート（人間用）

対話後、以下のシートに記入：

```markdown
| アイデア名 | Claude評価 | Codex評価 | 採用 | 理由 |
|---|---|---|---|---|
```

---

## ルール

- 各 Round の出力は `.claude/improvements/debate/` に保存
- ファイル名：`round1-claude.md`, `round1-codex.md`, `round2-claude.md`, `round2-codex.md`, `round3-final.md`
- 人間は最終判断者。AI同士の対話は参考情報。
