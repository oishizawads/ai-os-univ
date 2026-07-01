# Knowledge Card Template

Use this template when generating a knowledge card from a raw thread JSON.
Each card is saved as `cards/{topic_id}.md`.

---

## Template

```markdown
# {title}

| Field | Value |
|-------|-------|
| **Topic ID** | {topic_id} |
| **Author** | {author_display_name} ({author_tier}) |
| **Author Type** | {author_type: ADMIN/HOST/TOPIC} |
| **Votes** | {total_votes} |
| **Comments** | {comment_count} |
| **Posted** | {post_date as YYYY-MM-DD} |
| **Last Comment** | {last_comment_date as YYYY-MM-DD} |
| **Sticky** | {yes/no} |
| **Topic Type** | {topic_type or TBD — see CLASSIFICATION_RULES.md} |

## Summary
{2-3 sentences capturing the core content of this discussion.
What is the main point? What problem does it address or what information does it share?}

## Key Claims
- {Main claims, findings, or assertions made in the topic and high-value comments}
- {Include quantitative data when available (scores, timing, parameters)}

## Actionable Takeaways
- {Concrete things that can be applied to experiments or submissions}
- {Include specific parameters, configurations, or techniques mentioned}

## Notable Data/Resources
- {Datasets, notebooks, repos, or tools shared in the thread}
- {Format: [description](URL) or relative path to notebooks/{topic_id}/}

## Related
- **Topics**: {comma-separated topic_ids that are referenced or related}
- **Issues**: {related issue note filenames, if any}
```

---

## Generation Rules

1. **Read the full thread**: first_message + all comments + all replies
2. **Summary**: Capture the essence in 2-3 sentences. Focus on what makes this discussion valuable.
3. **Key Claims**: Extract factual claims and quantitative findings. Attribute to author if notable (e.g., host clarification). Include the author's `competition_ranking` if available in the JSON (e.g., "ranking 3", "ranking 60") — this helps assess the credibility of claims.
4. **Actionable Takeaways**: Only include items that directly inform experiments/submissions. Skip generic advice.
5. **Notable Data/Resources**: List all shared links (datasets, notebooks, external tools). Include Kaggle dataset/notebook URLs.
6. **Related Topics**: Extract topic IDs **only from actual URLs** in the thread (pattern: `/discussion/NNNNNN`). Do NOT infer or guess related topic IDs — only include IDs that are explicitly linked in the text.
7. **Votes**: Use the topic-level total_votes (from first_message.votes.total_votes or forum_topic.total_votes).
8. **Comments**: Use forum_topic.total_messages (NOT the length of the comments array, which may exclude replies).
9. **Skip low-value comments**: "Thank you", "Great work!", single emoji reactions — do not include in Key Claims or Takeaways.
10. **Preserve specifics**: Numbers, model names, parameter values, error messages — keep exact values.
11. **Topic Type**: If CLASSIFICATION_RULES.md has been designed, apply it. Otherwise write `TBD`.
12. **Language**: Write all cards in the same language. Default: the language specified in README.md. If not specified, use English. Technical terms (model names, parameter names, error messages) are kept in the original language.
13. **Last Comment fallback**: If there are no comments, use the post_date as Last Comment (never write N/A).
