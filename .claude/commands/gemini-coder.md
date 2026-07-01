---
allowed-tools: Bash(python C:/workspace/tools/gemini_coder.py:*)
argument-hint: [coding-or-research-task]
description: Delegate autonomous implementation/research to Gemini — applies file changes (yolo)
---

## Delegate

!`python C:/workspace/tools/gemini_coder.py "$ARGUMENTS"`

## Your task
NOTE: `gemini_coder.py` runs Gemini in autonomous "yolo" mode and MAY modify files
directly. The text above is Gemini's report (what it did + success/failure). Verify any
on-disk changes before relying on them.
