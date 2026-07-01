---
title: "Self-Managed Agent Principles (Synthesis)"
type: principle
domain: ai-os
tags: [self-management, backup, diagnostic, vocabulary]
created: 2026-05-03
source: "Multiple (Hermes-Backup, Diagnostic, Mercari-Vocab)"
---

## Summary
エージェント自身が自己の健全性を維持し、人間と同じコンテキストを共有するための補完的な原則。
「バックアップ」「自己診断」「共通言語」の3点を軸に、AI運用を盤石なものにする。

## Core Principles
- **AI-Managed Backup (Backup Skill)**: 作業ログ、生成コード、意思決定の履歴を、エージェントが自律的にバックアップし、不測のセッション終了や破損に備える。
- **Autonomous Diagnostics (Diagnostic)**: エラー発生時、AIが自らシステムの不整合や設定ミスを診断し、修正案を提示する。
- **Shared Professional Vocabulary (Mercari Vocab)**: 専門用語や組織固有の語彙をAIと共有し、コミュニケーションの「解像度」を一致させる。

## Decision Rules
- **Safety Rule**: 重要な変更を行う前には、AI自ら `backup-skill` を呼び出し、現在のスナップショットを保存させる。
- **Glossary Rule**: プロジェクト開始時、組織のエンジニア用語集（Mercari Vocab等）をAIにロードさせ、用語の定義を合わせる。

## Actionable Insights
- **Disaster Recovery**: `ai-os/shared/backups/` を設け、AIが定期的に重要な中間生成物を退避させる仕組みを構築する。
- **Diagnostic Loop**: 修正が3回失敗した場合は、強制的に `diagnostic` プロトコルに移行し、前提条件から洗い直す。
