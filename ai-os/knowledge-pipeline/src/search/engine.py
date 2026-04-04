"""Naive 全文テキスト検索エンジン"""
import re
from pathlib import Path


def _strip_frontmatter(text: str) -> str:
    return re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL).strip()


def _get_snippet(text: str, query_words: list[str], context: int = 100) -> str:
    """最初にマッチした箇所の前後context文字を返す"""
    lower = text.lower()
    for word in query_words:
        pos = lower.find(word.lower())
        if pos != -1:
            start = max(0, pos - context)
            end = min(len(text), pos + len(word) + context)
            snippet = text[start:end].replace("\n", " ").strip()
            return f"...{snippet}..."
    return text[:200].replace("\n", " ") + "..."


def search(query: str, vault_root: Path, top_k: int = 10, exclude_dirs: list[str] | None = None) -> list[dict]:
    """キーワードAND検索。スコア順のリストを返す"""
    exclude = set(exclude_dirs or ["_templates", "data"])
    query_words = [w for w in query.split() if w]
    if not query_words:
        return []

    results = []
    for md_path in vault_root.rglob("*.md"):
        if any(part in exclude for part in md_path.parts):
            continue
        if md_path.name.startswith("_"):
            continue

        try:
            text = md_path.read_text(encoding="utf-8")
        except Exception:
            continue

        body = _strip_frontmatter(text)
        lower_body = body.lower()
        lower_title = md_path.stem.lower()

        # AND検索: 全クエリ語がすべてヒットするか
        hit_count = sum(1 for w in query_words if w.lower() in lower_body)
        if hit_count < len(query_words):
            continue

        # タイトルマッチは2倍重み
        title_hits = sum(1 for w in query_words if w.lower() in lower_title)
        score = (hit_count + title_hits) / len(query_words)

        results.append({
            "path": md_path,
            "title": md_path.stem,
            "score": score,
            "snippet": _get_snippet(body, query_words),
            "relative": str(md_path.relative_to(vault_root)),
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
