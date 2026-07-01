# Issue Note Template

Issue notes are cross-topic theme documents that aggregate information scattered across multiple discussions.
Each issue is saved as `issues/{slug}.md`.

---

## Template

```markdown
# {Issue Title}

## Overview
{1-2 paragraphs describing the issue/theme and why it matters for the competition}

## Status
- **Severity**: {critical / important / informational}
- **Resolved**: {yes / no / partially}
- **Last Updated**: {YYYY-MM-DD}

## Related Topics
| Topic ID | Title | Relevance |
|----------|-------|-----------|
| {id} | {title} | {brief note on how this topic relates} |

## Key Findings
- {Aggregated findings from across all related topics}
- {Highlight contradictions or consensus between discussions}

## Action Items
- {What to do based on these findings}
- {Specific experiments or configurations to try}

## Timeline
| Date | Event |
|------|-------|
| {YYYY-MM-DD} | {What happened — initial report, fix released, etc.} |
```

---

## When to Create an Issue Note

1. **Same problem discussed in 3+ topics** — consolidate
2. **Host/admin clarification that changes understanding** — document the authoritative answer
3. **Competition-wide event** (metric change, data update, score shift) — track timeline
4. **Strategic theme** (training approach, inference optimization) — aggregate community findings

## Naming Convention

Use lowercase kebab-case slugs that describe the theme:
- `blackwell-kernel-compat.md`
- `score-instability.md`
- `metric-update-rescore.md`
- `training-approach-sft-grpo.md`
