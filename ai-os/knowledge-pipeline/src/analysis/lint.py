"""Wiki 健全性チェック（Lint）モジュール

以下を検出・報告する:
  1. 孤立記事     — wikiリンクもタグもない記事
  2. 壊れたリンク  — [[概念名]] が wiki/ に存在しない
  3. 孤立コンセプト — wiki/ にあるが記事から1件も参照されていない
  4. 記事密集タグ  — 上位タグと記事数（アンバランス検出）
  5. 新規コンセプト候補 — 複数記事で共起するが wikiページ未作成のリンク

出力: vault/reports/lint_{date}.md
"""
import logging
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    try:
        fm = yaml.safe_load(text[3:end].strip()) or {}
    except Exception:
        fm = {}
    return fm, text[end + 4:].strip()


def _extract_wikilinks(body: str) -> list[str]:
    raw = re.findall(r"\[\[([^\]|#]+)[^\]]*\]\]", body)
    return [r.strip() for r in raw if r.strip()]


def _load_vault(vault_root: Path, subdirs: list[str]) -> list[dict]:
    """指定サブディレクトリの全.mdを読み込んでメタデータリストを返す"""
    articles = []
    for subdir in subdirs:
        d = vault_root / subdir
        if not d.exists():
            continue
        for path in sorted(d.rglob("*.md")):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            fm, body = _parse_frontmatter(text)
            tags = fm.get("tags", [])
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]
            articles.append({
                "path": path,
                "title": fm.get("title") or path.stem,
                "tags": [str(t) for t in (tags or [])],
                "wikilinks": _extract_wikilinks(body),
                "subdir": subdir,
            })
    return articles


def run_lint(cfg: dict) -> Path:
    """Vault全体をLintして結果レポートをファイルに保存"""
    vault_root = Path(cfg["vault"]["path"])
    wiki_dir = vault_root / cfg["vault"].get("wiki_dir", "wiki")
    reports_dir = vault_root / cfg["vault"].get("reports_dir", "reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    scan_subdirs = [
        cfg["vault"].get("blogs_dir", "blogs"),
        cfg["vault"].get("papers_dir", "papers"),
        cfg["vault"].get("notebooks_dir", "notebooks"),
    ]

    articles = _load_vault(vault_root, scan_subdirs)
    logger.info("Loaded %d articles for lint", len(articles))

    # wiki/ に存在するコンセプト名セット
    existing_wiki = {p.stem for p in wiki_dir.glob("*.md") if not p.stem.startswith("_")} if wiki_dir.exists() else set()

    # 全記事から参照されているコンセプト集計
    concept_ref_count: Counter = Counter()
    for a in articles:
        for link in a["wikilinks"]:
            concept_ref_count[link] += 1

    # --- 各チェック ---

    # 1. 孤立記事（wikiリンクもタグもない）
    isolated = [a for a in articles if not a["wikilinks"] and not a["tags"]]

    # 2. 壊れたリンク（wiki/に存在しない概念への参照）
    broken_links: dict[str, list[str]] = defaultdict(list)
    for a in articles:
        for link in a["wikilinks"]:
            if link not in existing_wiki:
                broken_links[link].append(a["title"])

    # 3. 孤立コンセプト（wiki/にあるが記事から参照されていない）
    orphan_wiki = [c for c in existing_wiki if concept_ref_count.get(c, 0) == 0]

    # 4. タグ分布（上位10件）
    tag_counter: Counter = Counter()
    for a in articles:
        for t in a["tags"]:
            tag_counter[t] += 1

    # 5. 新規コンセプト候補（2件以上から参照されているがwikiページ未作成）
    new_candidates = [
        (concept, count)
        for concept, count in concept_ref_count.most_common()
        if concept not in existing_wiki and count >= 2
    ]

    # --- レポート生成 ---
    date_str = datetime.now().strftime("%Y-%m-%d")
    lines = [
        f"---\ntitle: Wiki Lint Report {date_str}\ntype: report\ndate: {date_str}\n---\n",
        f"# Wiki Lint Report — {date_str}\n",
        f"- 検査記事数: {len(articles)}\n",
        f"- Wikiコンセプト数: {len(existing_wiki)}\n\n",
    ]

    # 1
    lines.append(f"## 1. 孤立記事（{len(isolated)}件）\n")
    lines.append("wikiリンクもタグも持たない記事。整形が不完全な可能性あり。\n\n")
    for a in isolated[:20]:
        lines.append(f"- [[{a['title']}]] ({a['subdir']})\n")
    if len(isolated) > 20:
        lines.append(f"- ...他 {len(isolated) - 20} 件\n")
    lines.append("\n")

    # 2
    lines.append(f"## 2. 壊れたリンク（{len(broken_links)}件）\n")
    lines.append("記事から参照されているがwiki/にページが存在しないコンセプト。`--compile` で生成可能。\n\n")
    for concept, refs in sorted(broken_links.items(), key=lambda x: -len(x[1]))[:30]:
        lines.append(f"- **[[{concept}]]** — {len(refs)}記事から参照\n")
    if len(broken_links) > 30:
        lines.append(f"- ...他 {len(broken_links) - 30} 件\n")
    lines.append("\n")

    # 3
    lines.append(f"## 3. 孤立コンセプト（{len(orphan_wiki)}件）\n")
    lines.append("wiki/にページがあるが記事から1件も参照されていない。削除候補または記事側の更新が必要。\n\n")
    for c in sorted(orphan_wiki)[:20]:
        lines.append(f"- [[{c}]]\n")
    lines.append("\n")

    # 4
    lines.append("## 4. タグ分布（上位15件）\n\n")
    lines.append("| タグ | 記事数 |\n|---|---|\n")
    for tag, count in tag_counter.most_common(15):
        lines.append(f"| {tag} | {count} |\n")
    lines.append("\n")

    # 5
    lines.append(f"## 5. 新規コンセプト候補（{len(new_candidates)}件）\n")
    lines.append("複数記事から参照されているがwikiページ未作成。`--compile` で一括生成できる。\n\n")
    lines.append("| コンセプト | 参照数 |\n|---|---|\n")
    for concept, count in new_candidates[:30]:
        lines.append(f"| [[{concept}]] | {count} |\n")
    lines.append("\n")

    report_text = "".join(lines)
    out_path = reports_dir / f"lint_{date_str}.md"
    out_path.write_text(report_text, encoding="utf-8")

    logger.info("Lint report saved: %s", out_path)
    _print_summary(isolated, broken_links, orphan_wiki, new_candidates)
    return out_path


def _print_summary(isolated, broken_links, orphan_wiki, new_candidates):
    print("\n=== Lint Summary ===")
    print(f"  孤立記事:           {len(isolated)} 件")
    print(f"  壊れたリンク:       {len(broken_links)} 種")
    print(f"  孤立コンセプト:     {len(orphan_wiki)} 件")
    print(f"  新規候補コンセプト: {len(new_candidates)} 件")
    if new_candidates:
        top = new_candidates[:5]
        print(f"  上位候補: {', '.join(c for c, _ in top)}")
    print()
