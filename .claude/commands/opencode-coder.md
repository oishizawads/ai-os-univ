---
allowed-tools: Bash(python C:/workspace/tools/opencode_coder.py:*)
argument-hint: [coding-task]
description: Delegate implementation to OpenCode Go (qwen3.6-plus) — direct wrapper, stdout
---

## Delegate

!`python C:/workspace/tools/opencode_coder.py "$ARGUMENTS"`

## Your task
The text above is OpenCode's stdout (code-first response). Relay a 1-2 sentence
summary to the user. OpenCode runs with skip-permissions and may touch files —
verify any on-disk changes before relying on them.
