---
title: "Ankh.md: Multi-Agent Swarm Protocol"
type: framework
domain: agentic-workflow
tags: [ankh, swarm, hermes, map, coordination]
created: 2026-05-03
source: "https://github.com/Abruptive/Ankh.md"
---

## Summary
Hermes Agentエコシステムのために設計された、謎めいたマルチエージェント・スウォーム（群れ）フレームワーク。
**Multi-Agent Protocol (MAP)** を通じて、複数のエージェントを分散・強調させ、ディレクトリ固有の文脈（Scoped Identity）で動作させる。

## Core Principles
- **Multi-Agent Protocol (MAP)**: エージェント間の通信と相互運用性を可能にする型定義されたメッセージスキーマ。
- **Scoped Identity**: エージェントを特定のディレクトリやプロジェクトに紐付け、グローバル設定を汚染せずに専門特化させる。
- **Network-Efficient Orchestration**: 複数のHermesゲートウェイを単一のゲートウェイで束ね、効率的にタスクを分散実行する。
- **Task-Agnostic Workflow (TAW)**: 特定のタスクに縛られず、ディレクトリの文脈（.agent 構成）を読み取って自律的に人格と行動を調整する。

## Decision Rules
- **Summoning Rule**: 専門的な知識が必要なプロジェクトでは、`.agent/` フォルダを配置し、特化型エージェントを「召喚（Summon）」する。
- **MAP Compliance**: エージェント間のデータ共有やタスク委譲は、必ずMAPスキーマに従って構造化データ（JSONC）で行う。

## Key Components
- **`Ankh.md`**: フレームワークの入り口と基本定義。
- **`AUTONOMOUS_ORCHESTRATION_FRAMEWORK.md`**: 自律的な調整とオーケストレーションのロジック。
- **`.agent/agent.jsonc`**: スコープされたエージェントの「魂（Identity）」と指示を定義するファイル。

## Actionable Insights
- **Agent Governance**: `.agent/` フォルダをGit管理し、プロジェクトに最適化されたエージェント設定（Persona, Skills）をチームで共有する。
- **Distributed Reasoning**: 難易度の高い課題に対し、複数の特化型エージェントをMAP経由で連携させ、多角的な視点から解決策を導き出す。
