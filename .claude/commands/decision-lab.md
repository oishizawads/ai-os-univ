---
allowed-tools: Bash(rg:*), Bash(python:*), Read(C:/workspace/decision-lab/**)
argument-hint: [analysis-task]
description: Inspect or plan a decision-lab workflow for a data science task
---

# decision-lab

## Objective
Use `decision-lab` as a structured framework for analysis tasks where robustness matters more than a single fast answer.

## When to Use
- The task is data science rather than product coding.
- One analytical path is likely to be misleading.
- You want multiple model assumptions or parallel approaches compared.
- The output should include confidence, disagreement, or next experiments.

## Workflow
1. Read `decision-lab/README.md`.
2. Inspect the closest existing decision-pack under `decision-lab/decision-packs/`.
3. Decide whether the task should:
   - reuse an existing decision-pack
   - fork and adapt one
   - scaffold a new one
4. Summarize:
   - target problem
   - likely decision-pack starting point
   - required environment
   - expected artifacts
   - whether Docker is required immediately

## Guardrails
- Do not recommend decision-lab for trivial coding tasks.
- Prefer adapting an existing decision-pack before designing a new one from scratch.
- Call out validation and convergence requirements explicitly.
