---
allowed-tools: Bash(python C:/workspace/tools/codex_coder.py:*)
argument-hint: [analysis-or-review-task]
description: Delegate READ-ONLY analysis/review to Codex (gpt-5.4) — does NOT modify files
---

## Delegate

!`python C:/workspace/tools/codex_coder.py "$ARGUMENTS"`

## Your task
NOTE: `codex_coder.py` runs Codex in a **read-only** sandbox (`-s read-only`). It does
NOT apply file changes — use it for review, diagnosis, and second opinions, not for
implementation. The text above is Codex's stdout; relay a concise summary of its findings.
