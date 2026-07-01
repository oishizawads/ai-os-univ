# Topic Type Classification Rules

## Status: NOT YET DESIGNED

This file should be designed after fetching and reviewing the first 20 discussions.
Until then, cards should use `TBD` for the Topic Type field.

---

## Candidate Topic Types

The following types are common across Kaggle competitions. After reviewing the first batch of discussions, select the types that apply and add competition-specific types as needed.

| Type | Description | Typical Signal |
|------|-------------|---------------|
| `official_rule` | Official rules, announcements | author_type=ADMIN/HOST, is_sticky |
| `host_clarification` | Host answering questions | HOST in comments, Q&A format |
| `environment_issue` | GPU/CUDA/VRAM/package issues | Error messages, package names |
| `metric_issue` | Metric bugs, scoring behavior | "metric", "score", "evaluation" |
| `dataset_issue` | Data quality, labels, format | "data", "label", "hallucination" |
| `baseline_analysis` | Base model behavior analysis | "baseline", "zero-shot", "base model" |
| `modeling_idea` | Training/architecture strategies | "LoRA", "SFT", "GRPO", "fine-tune" |
| `inference_optimization` | Speed/memory optimization | "vLLM", "throughput", "VRAM" |
| `submission_issue` | Submission format, errors | "submit", "zip", "adapter" |
| `leaderboard_shift` | Score changes, LB issues | "score dropped", "rescore" |
| `resource_link` | Shared notebooks/datasets | Links to kaggle.com datasets/notebooks |
| `community_experiment` | Participant experiment reports | Score reports, comparisons |
| `getting_started` | Tutorials, setup guides | "getting started", "beginner" |
| `team_formation` | Looking for teammates | team_up_info populated |

## Design Instructions

After reviewing the first 20 cards:

1. **Remove** types that don't appear in this competition
2. **Add** competition-specific types (e.g., `problem_type_analysis` for pattern recognition competitions)
3. **Write concrete criteria** for each type — what specific signals in the thread trigger this classification
4. **Allow multiple types** per topic (comma-separated)
5. **Define a primary type** — the first listed type is the primary
6. **Write a `question` 乱用防止ルール** — `question` はフォールバック。エラー/手法/メトリック/提出に関する質問はそちらのタイプを優先。`question` を primary にしてよいのは他タイプに明確に該当しない場合のみ
7. **Write a primary type 選定基準** — primary typeはそのdiscussionの最も情報価値が高い側面を反映する。具体例を付けること
