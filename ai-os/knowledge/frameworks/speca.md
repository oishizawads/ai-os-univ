---
title: "SPECA: Specification-Anchored Security Audit Framework"
type: framework
domain: coding
tags: [security, auditing, verification, formal-properties, spec-anchored]
created: 2026-05-05
source: "Beyond Code Reasoning: A Specification-Anchored Audit Framework for Expert-Augmented Security Verification (arXiv:2604.26495)"
---

## Summary
SPECA (Specification-Anchored security audit) は、コードのパターンマッチングではなく、自然言語の仕様書（Specification）から導出された「明示的・型付きセキュリティプロパティ」を起点に監査を行うフレームワーク。仕様が要求するインバリアント（不変条件）と実装の乖離を、構造化された「証明試行（Proof-attempt reasoning）」によって検出する。

## Core Principles
- **Specification Anchoring**: 監査の起点をコードではなく、プロトコル文書やREADMEなどの自然言語仕様に置く。
- **Property-Driven Auditing**: 仕様から抽出した型付きセキュリティプロパティを語彙として共有し、それに基づいた監査を行う。
- **Proof-Attempt Reasoning**: 単なるパターン検出ではなく、実装がプロパティを遵守しているかを「証明しようとする（およびその失敗を追跡する）」論理的推論を行う。

## Decision Rules
- **適用条件**: 
  - プロトコルスタック、コンセンサス実装、暗号ライブラリなど、仕様書が厳密に存在するシステム。
  - コードレベルのパターンだけでは検出しにくい、論理的脆弱性を探す場合。
  - 複数の異なる実装（例：異なる言語でのEthereumノード）を同じ基準で比較監査する場合。
- **非適用条件**:
  - 仕様が不明確または存在しない、アドホックなスクリプト。
  - バッファオーバーフローなど、仕様に関係なく発生する純粋な実装バグのみを対象とする場合（従来の静的解析ツールの方が効率的）。

## Procedure
1. **Specification Analysis**: 自然言語の仕様を分析し、意図された不変条件と正当性条件を理解する。
2. **Property Extraction**: 仕様から形式的・型付きのセキュリティプロパティ（Properties）を抽出・定義する。
3. **Structured Audit (Proof-Attempt)**: 各プロパティに対し、コードがそれを満たしているか「証明」を試みる。
4. **Root Cause Diagnosis**: 検証失敗や偽陽性を「プロパティ生成・コード読解・推論」のどのフェーズで発生したか特定し、分類する。

## Anti-patterns
- **Code-Local Reasoning**: 仕様を無視してコード内のパターン（例：Reentrancy, Integer Overflow）のみを追跡すること。仕様上の制約による脆弱性を見逃す。
- **Opaque False Positives**: ツールが「なぜ」警告を出したか不明瞭な状態。SPECAでは、推論プロセスのどの段階（仕様の誤解か実装の誤読か）でエラーが起きたかを追跡可能にする。

## Example
EthereumのFusaka Auditにおいて、従来のパターンベースのツールが見逃した「仕様が要求する特定の状態遷移の不備」を、仕様から導出したプロパティに基づき4つの新規バグとして発見。

## Eval
- 監査対象の仕様から明示的なプロパティが抽出されているか？
- 各脆弱性指摘が、どのプロパティに違反しているか紐付けられているか？
- 偽陽性が発生した際、その原因が「仕様の解釈ミス」か「コードの読み間違い」か特定されているか？
