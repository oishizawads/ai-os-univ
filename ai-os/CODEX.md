# AI OS - CODEX.md

## Purpose
Codex は、Claude Code の補助役として使う技術監査・差分レビュー・調査担当である。
Claude が全体進行と意思決定支援を担い、Codex は局所的・技術的な精査を担う。

## Primary Responsibilities
- 差分レビュー
- train / inference / config の整合性監査
- 例外や不具合の原因候補整理
- 大きなコードベースの横断確認
- リファクタ候補の比較
- 実装上の危険箇所の指摘

## Do Not Use Codex For
- ふわっとした要件整理
- 会議メモの要約
- ビジネス論点の優先順位づけ
- まだ論点が固まっていない段階の壁打ち

## Claude vs Codex

### Claude Code
- 問題設定
- 要件整理
- 実験・案件の進行管理
- ドキュメント更新
- 方針選定
- skill / agent の使い分け

### Codex
- コード精査
- 技術的妥当性の監査
- 変更差分の影響範囲洗い出し
- バグ原因の切り分け
- 実装の危険性チェック

## When to Invoke Codex
- train.py と inference.py の整合が不安
- validation や leakage の見落としが怖い
- 差分が大きく、破壊範囲を洗いたい
- 例外原因が複数ありそう
- リファクタ案を比較したい
- 本番投入前に技術的監査をしたい

## Handoff Template
Codex に依頼する時は、以下を明示する。

- Objective:
- Files to inspect:
- What changed:
- What to focus on:
- Constraints:
- Output format:

## Standard Review Axes
- correctness
- reproducibility
- maintainability
- inference parity
- leakage risk
- config consistency
- logging / observability
- unnecessary complexity
- merge risk

## Expected Output
- Summary
- Critical issues
- Medium issues
- Nice to have
- Suggested fixes
- Safe to adopt as-is? (Yes / No / With conditions)