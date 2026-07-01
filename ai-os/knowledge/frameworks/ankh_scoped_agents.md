---
title: "Scoped Agentic Workflows (Ankh.md)"
type: framework
domain: agentic-workflow
tags: [scoped-agents, ankh, isolation]
created: 2026-05-03
source: "https://github.com/Abruptive/Ankh.md"
---

## Summary
プロジェクト固有の隔離されたAIエージェントを作成し、コードベース内に共存させるためのフレームワーク。
コンテキストの汚染を防ぎ、ディレクトリ単位での専門特化（Persona, Tools, Memory）を可能にする。

## Core Principles
- **Contextual Isolation**: エージェントを特定のフォルダにスコープし、無関係なプロジェクトからの情報の混入を防ぐ。
- **Configuration Inheritance**: グローバルなベースライン設定を、ローカルの `config.yaml` で「外科的に」上書きする。
- **Specialization over Generalization**: 単一の巨大な汎用エージェントよりも、複数の特化型エージェント（Swarm）を推奨。
- **Seamless Context Awareness**: 作業ディレクトリに応じて、AIインターフェースが自動的に人格と能力を切り替える。

## Decision Rules
- **Scoping Rule**: プロジェクトが独自のドメイン知識、固有のツール、またはプライベートなメモリを必要とする場合、ローカルに `.agent/` 構成を作成する。
- **Override Rule**: 技術的設定（モデル、ツール）には `config.yaml` を使い、人格や指示には `agent.jsonc` を使う。
- **Skill Rule**: プロジェクト固有のロジックは `.agent/skills/` に配置し、グローバルエージェントの能力セットを肥大化させない。

## Procedure
1. **Initialize**: プロジェクトのルートに `.agent/` ディレクトリを作成。
2. **Configure Identity**: `.agent/agent.jsonc` でエージェントのタイトル、プロンプト、指示を定義。
3. **Define Capabilities**: `.agent/config.yaml` でプロジェクト固有のツールやモデルの上書きを定義。
4. **Implement Skills**: `.agent/skills/` にカスタムスクリプトやロジックを追加。
5. **Execute**: プロジェクトフォルダ内でエージェントを起動し、スコープされたインスタンスを有効化。

## Anti-patterns
- **Cross-Pollination**: 無関係なプロジェクト間で同じエージェントセッションやメモリを使い回す。
- **Global Bloat**: プロジェクト固有のスキルをグローバル設定に追加してしまう。
- **Manual Context Loading**: 毎回手動でプロジェクト構造を説明する（永続的なスコープ構成を使わない）。
