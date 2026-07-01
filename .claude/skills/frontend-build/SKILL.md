---
name: frontend-build
description: Web/アプリUI実装の正典（オンデマンド・委譲前提）。DSデモは Streamlit/Gradio を既定、本格Webは必要時のみ。実装はCodex/OpenCodeへ、設計は ui-ux-design。
---

# Frontend Build

## Mission
[[ui-ux-design]] で決めた設計を「動くUI」にする層。ただし**重実装は委譲**し、自分は技術選定・仕様・レビューを担う。フロントの内製マスターは目指さない。

## Rules
- **既定はStreamlit（or Gradio）**: DS成果物のデモ/ダッシュボードはこれで十分速い。MTJの `app/` もこの型。**Reactなど本格Webは「クライアントが本番UIを求める」等の明確な理由があるときだけ**。
- **状態とデータの流れを先に決める**: 入力（フィルタ/シナリオ）→ 計算（[[python-style]] の `src/` 関数）→ 表示。UIロジックと計算ロジックを混ぜない。
- **計算は src/ に置きUIは薄く**: 画面コードはオーケストレーションだけ。再利用ロジックは関数化（[[notebook-workflow]] と同じ思想）。
- **実装は委譲**: 雛形・コンポーネント量産は OpenCode/Codex に投げる。仕様（画面・入出力・状態）を明文で渡す。
- **パス/IOは [[path-io]]**、秘密情報は [[safe-data-handling]]（キーをフロントに埋めない）。

## Workflow
1. [[ui-ux-design]] の設計を受け取る。
2. 技術選定（Streamlit / Gradio / Web）を理由つきで決める。
3. 画面・状態・入出力の仕様を書く → 実装をエージェントに委譲。
4. 計算ロジックを `src/` に分離して結線。
5. [[ui-polish]]（仕上げ）→ [[ship-harden]]（欠損/エラー/秘密情報）で締める。

## 精査メモ（2026-06-18）
コミュニティに強い上位互換は見当たらず。Streamlit既定＋計算ロジックを `src/` に分離＋重実装は委譲、という routing 層として**自前維持が適切**。本格Web案件が来たら shadcn/Tailwind系の設計スキル導入を再検討。

## Guardrails
- **PoCに本番級の作り込みをしない**。動いて読めれば十分。スコープは [[work-implementation]] で確認。
- 委譲した実装も**自分でレビュー**（出来を判断できることが「できる」の定義）。
- 巨大UIや独自デザインシステムを学生案件で抱え込まない。
