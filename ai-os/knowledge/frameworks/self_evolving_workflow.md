---
title: "Self-Evolving Multi-Agent Workflow (Synthesis)"
type: framework
domain: ai-os
tags: [memory, context, skill-forge, scoped-agents]
created: 2026-05-03
source: "Multiple (Vibeyard, Plur, Aegis, Ankh, Skill-Forge)"
---

## Summary
単一のチャットUIから脱却し、**「メモリの永続化」「決定論的なコンテキスト提供」「自己進化するスキルセット」**を統合した、自律的なAI運用OSの全体像。
エージェントを「一度きりのアシスタント」ではなく、組織のコンテキストを学習し続ける「デジタル社員」として扱う。

## Core Principles
- **Determinism over Fuzzy RAG**: 曖昧なベクトル検索（RAG）だけに頼らず、依存関係グラフ（DAG）に基づき「確実に必要な文書」をAIに渡す。
- **Persistent Personal Memory**: エージェントへの「指摘」や「好み」をツール間で共有し、使えば使うほど賢くなるローカルメモリ層（Plur等）を維持する。
- **Autonomous Skill Acquisition**: 繰り返される成功パターンを、AI自らが再利用可能な「スキル（SKILL.md）」として定義・テスト・保存する。
- **Scoped Identity**: フォルダ単位でエージェントの人格・能力を最適化し、コンテキストの汚染を防ぎつつ専門性を高める。

## Decision Rules
- **Memory Rule**: AIに対する修正や定型的な指示は、会話で終わらせず `engrams/` (assertions) として保存し、全エージェントで共有する。
- **Context Rule**: アーキテクチャ上重要なファイル（Core Logic）を編集する際は、必ず関連する設計書（DESIGN.md）を「決定論的」にロードさせる。
- **Skill Forge Rule**: 3回以上繰り返した定型作業は、AIに「Skill Forge」を指示し、再利用可能なコマンド化を試行させる。

## Procedure
1. **Initialize Context Graph**: プロジェクト構造を解析し、ファイル間の依存関係と対応するドキュメントをマッピング（Aegis/SocratiCode）。
2. **Deploy Scoped Agent**: ディレクトリごとにPersona（性格）とToolセットを定義した `.agent/` を構築（Ankh）。
3. **Session with Persistence**: 全てのセッションでPlur等のメモリ層をロードし、過去の教訓を反映。
4. **Post-Task Refinement**: 作業完了後、成功パターンを抽出して `ai-os/knowledge/` または `skills/` に反映。

## Actionable Configurations
- **Vibeyard Style**: 並列でエージェントを動かし、進捗をテレメトリ（Token, Cost, Vibe）で監視。
- **SocratiCode Search**: 大規模リポジトリでは「読み込む前に検索（Search-before-reading）」を徹底し、依存関係をグラフで把握。
- **Crazyrouter Logic**: 安価なモデル（DeepSeek/Qwen）でルーチンを回し、難易度の高い推論時のみ上位モデル（Claude/Hermes）に切り替える。
