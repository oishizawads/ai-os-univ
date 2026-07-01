---
name: notebook-export
description: notebook の学びを整理し、再利用可能な形へ切り出す。
---

# Notebook Export

## Mission
notebook の実験や検証を、再利用できるコードと記録に分離する。

## Workflow
1. notebook の目的と結論を短くまとめる。
2. 再利用できるコード、実験専用コード、捨てるコードを分ける。
3. `src` に移す候補と、その理由を出す。
4. 記録更新が必要なファイルを列挙する。

## Guardrails
- 動いたセル順をそのまま本番コードにしない。
- 再利用単位は関数やモジュールで切る。
- 実験用の一時処理は残しすぎない。

## Output
- Objective
- Key findings
- Reusable code candidates
- What should move to src
- What should stay experimental
- Record updates needed
