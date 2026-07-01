# AI OS Skills

Skills used by the ai-os workspace.

## Active Skills
| Skill | Purpose |
|-------|---------|
| `bug-investigation/` | エラー原因の切り分け |
| `experiment-workflow/` | 実験の設計→検証→記録 |
| `notebook-export/` | notebookの学び切り出し |
| `review-exp/` | 実験コードのレビュー |
| `slides-maker/` | 日本語スライド作成 |
| `submit-monitor/` | submission前後の検証 |
| `survey-papers/` | 論文・既知解法調査 |
| `work-implementation/` | 業務開発の標準手順 |

## Engineering Skills
| Skill | Purpose |
|-------|---------|
| `engineering/` | エンジニアリング系スキル集 |

## Third-Party Skills
External skills from the community. See `third_party/` for the full list.
These are not actively maintained by this workspace.

## Deprecated Skills
Skills that are no longer relevant. See `deprecated/`.

## Adding a New Skill
1. Create a directory: `mkdir new-skill-name/`
2. Add `SKILL.md` with frontmatter:
   ```yaml
   ---
   name: new-skill-name
   description: When and how to use this skill
   ---
   ```
3. Add step-by-step instructions in the body.
