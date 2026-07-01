---
title: "Structured Visual Identity (design.md)"
type: framework
domain: design-system
tags: [design-tokens, agent-communication, design-md]
created: 2026-05-03
source: "https://github.com/google-labs-code/design.md"
---

## Summary
デザインシステムをAIエージェントに伝えるための仕様。
機械可読なトークン（YAML）と人間可読な理論（Markdown）を組み合わせることで、AIがブランドの「Vibe」と「仕様」を正確に理解できるようにする。

## Core Principles
- **Dual-Layer Communication**: YAMLで正確な値（トークン）を伝え、Markdownでその意図（理論）を伝える。
- **Persistence**: デザインシステムを `DESIGN.md` としてコード管理し、エージェントに長期的な理解を与える。
- **Normative Truth**: トークンは「値」の正解であり、散文は「適用ロジック」と「Vibe」の正解である。
- **Automated Validation**: リンターを使用して、アクセシビリティ（コントラスト比等）や参照の整合性を自動検証する。

## Decision Rules
- **Token Rule**: 再利用される値（色、余白、フォント）は、必ずフロントマターのトークンとして定義する。
- **Rationale Rule**: 各デザインカテゴリ（色、タイポグラフィ等）には、意図を説明する散文セクションを設ける。
- **Reference Rule**: コンポーネントはハードコードされた値ではなく、必ずトークン（例: `{colors.primary}`）を参照する。

## Procedure
1. **Define Tokens**: `colors`, `typography`, `rounded`, `spacing` などのYAMLフロントマターを作成。
2. **Write Rationale**: Markdownセクションを作成し、ブランドの「Vibe」と使用ルールを記述。
3. **Map Components**: 基本トークンを参照するコンポーネント固有のトークン（例: `button-primary`）を定義。
4. **Validate**: リンターを実行し、コントラストエラーや参照切れをチェック。
5. **Consume**: 実装エージェントに `DESIGN.md` を渡し、UI生成のガイドとする。

## Anti-patterns
- **Hardcoded Values**: コンポーネント定義で直接16進数やピクセル値を使用する。
- **Prose-Only Design**: 言葉だけでデザインを説明し、AIの実装にばらつきが出る。
- **Token-Only Design**: 文脈なしに値だけを提供し、「魂のない」または誤った適用を招く。
- **Out-of-Order Sections**: 標準的なセクション順序から外れ、エージェントのパースを混乱させる。
