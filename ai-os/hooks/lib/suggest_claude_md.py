"""PostToolUse hook (Edit/Write): print actionable CLAUDE.md update suggestions."""

import json
import sys
from pathlib import Path


def normalize_path(raw: str) -> Path:
    if not raw:
        return Path()
    if raw.startswith('/c/'):
        raw = 'C:/' + raw[3:]
    return Path(raw)


def extract_file_path(payload: dict) -> Path:
    tool_input = payload.get('tool_input', {}) or {}
    raw = tool_input.get('file_path') or tool_input.get('path') or ''
    return normalize_path(raw)


def find_nearest_claude_md(start: Path):
    if not start:
        return None
    current = start.parent if start.is_file() else start
    for parent in [current, *current.parents]:
        candidate = parent / 'CLAUDE.md'
        if candidate.exists():
            return candidate
    return None


def classify_suggestion(file_path: Path, claude_md: Path):
    suggestions = []
    try:
        rel = file_path.relative_to(claude_md.parent)
    except Exception:
        return suggestions

    rel_text = str(rel).replace('\\', '/')
    top = rel.parts[0] if rel.parts else ''
    content = claude_md.read_text(encoding='utf-8', errors='ignore')

    if file_path.name == 'CLAUDE.md':
        return suggestions

    if top and top not in content:
        suggestions.append(
            f'Consider adding `{top}/` to the directory or workflow rules in {claude_md}.'
        )

    if top == 'research':
        suggestions.append(
            f'Consider documenting how `research/` should be read and updated in {claude_md}.'
        )

    if top == 'experiments':
        suggestions.append(
            f'Consider refreshing experiment workflow guidance in {claude_md} for files under `{rel_text}`.'
        )

    if top == '.steering':
        suggestions.append(
            f'Consider mentioning steering artifacts or planning expectations in {claude_md}.'
        )

    if file_path.suffix in {'.sh', '.py'} and 'hooks' in rel.parts:
        suggestions.append(
            f'Consider documenting hook behavior or maintenance rules in {claude_md}.'
        )

    return suggestions


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return

    file_path = extract_file_path(payload)
    if not file_path:
        return

    claude_md = find_nearest_claude_md(file_path)
    if claude_md is None:
        print(f'[suggest-claude-md] edited: {file_path}')
        print('[suggest-claude-md] no nearby CLAUDE.md found')
        return

    suggestions = classify_suggestion(file_path, claude_md)
    if not suggestions:
        return

    print(f'[suggest-claude-md] edited: {file_path}')
    print(f'[suggest-claude-md] nearest CLAUDE.md: {claude_md}')
    for line in suggestions:
        print(f'[suggest-claude-md] {line}')


if __name__ == '__main__':
    main()
