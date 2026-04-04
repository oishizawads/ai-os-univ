"""知識グラフ定量分析モジュール

Vault内の全.mdファイルをパースし、NetworkXでグラフ構築・分析する。
"""
import logging
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

import networkx as nx
import yaml

logger = logging.getLogger(__name__)


# --- パース関数 ---

def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """YAMLフロントマターとbodyを分離して返す"""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_str = text[3:end].strip()
    body = text[end + 4:].strip()
    try:
        fm = yaml.safe_load(fm_str) or {}
    except Exception:
        fm = {}
    return fm, body


def _extract_wikilinks(body: str) -> list[str]:
    """[[wikilink]] パターンをすべて抽出する"""
    # [[link|alias]] 形式にも対応
    raw = re.findall(r"\[\[([^\]|#]+)[^\]]*\]\]", body)
    return [r.strip() for r in raw if r.strip()]


def _extract_tags(fm: dict) -> list[str]:
    """フロントマターのtagsフィールドを抽出する（リスト・文字列両対応）"""
    tags = fm.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    elif isinstance(tags, list):
        tags = [str(t).strip() for t in tags if t]
    else:
        tags = []
    return tags


# --- グラフ構築 ---

def build_graph(vault_path: Path) -> tuple[nx.DiGraph, list[dict]]:
    """Vault全.mdをパースしてグラフを構築する。

    ノード種別:
      - article : .mdファイル
      - tag     : frontmatterのtag
      - concept : [[wikilink]]で参照された概念

    エッジ:
      - article → tag    (has_tag)
      - article → concept (links_to)

    Returns:
        (graph, articles_meta)
        articles_meta: [{"path": Path, "title": str, "tags": [...], "wikilinks": [...]}]
    """
    G = nx.DiGraph()
    articles_meta = []

    md_files = sorted(vault_path.rglob("*.md"))
    logger.info("Scanning %d .md files in vault: %s", len(md_files), vault_path)

    for md_path in md_files:
        try:
            text = md_path.read_text(encoding="utf-8", errors="ignore")
        except OSError as e:
            logger.warning("Read error: %s: %s", md_path, e)
            continue

        fm, body = _parse_frontmatter(text)
        tags = _extract_tags(fm)
        wikilinks = _extract_wikilinks(body)

        # タイトル：frontmatterのtitle → ファイル名ステムの順
        title = fm.get("title") or md_path.stem

        article_id = str(md_path.relative_to(vault_path))
        G.add_node(article_id, kind="article", title=title, path=str(md_path))

        for tag in tags:
            tag_id = f"tag::{tag}"
            G.add_node(tag_id, kind="tag", label=tag)
            G.add_edge(article_id, tag_id, rel="has_tag")

        for link in wikilinks:
            concept_id = f"concept::{link}"
            G.add_node(concept_id, kind="concept", label=link)
            G.add_edge(article_id, concept_id, rel="links_to")

        articles_meta.append({
            "path": md_path,
            "id": article_id,
            "title": title,
            "tags": tags,
            "wikilinks": wikilinks,
        })

    logger.info(
        "Graph built: %d nodes, %d edges (%d articles)",
        G.number_of_nodes(), G.number_of_edges(), len(articles_meta),
    )
    return G, articles_meta


# --- 分析関数 ---

def analyze(G: nx.DiGraph, articles_meta: list[dict], cfg: dict) -> dict:
    """グラフを分析して結果dictを返す"""

    # --- タグ使用頻度 ---
    tag_counter: Counter = Counter()
    for art in articles_meta:
        for tag in art["tags"]:
            tag_counter[tag] += 1

    # --- 最多参照概念（wikilinks in-degree） ---
    concept_nodes = [n for n, d in G.nodes(data=True) if d.get("kind") == "concept"]
    concept_degree = {
        G.nodes[n]["label"]: G.in_degree(n)
        for n in concept_nodes
    }
    top_concepts = sorted(concept_degree.items(), key=lambda x: -x[1])[:20]

    # --- カバレッジギャップ（taxonomyで未使用のタグ） ---
    taxonomy = cfg.get("tags", {}).get("taxonomy", [])
    used_tags = set(tag_counter.keys())
    unused_taxonomy = [t for t in taxonomy if t not in used_tags]

    # --- 孤立記事（リンク数 = out_degree < 2） ---
    article_nodes = [n for n, d in G.nodes(data=True) if d.get("kind") == "article"]
    isolated = []
    for node in article_nodes:
        out_deg = G.out_degree(node)
        if out_deg < 2:
            isolated.append({
                "id": node,
                "title": G.nodes[node].get("title", node),
                "links": out_deg,
            })

    # --- 総統計 ---
    tag_nodes = [n for n, d in G.nodes(data=True) if d.get("kind") == "tag"]
    total_links = sum(len(a["wikilinks"]) + len(a["tags"]) for a in articles_meta)
    avg_links = total_links / len(articles_meta) if articles_meta else 0.0

    return {
        "tag_ranking": tag_counter.most_common(30),
        "top_concepts": top_concepts,
        "unused_taxonomy": unused_taxonomy,
        "isolated_articles": sorted(isolated, key=lambda x: x["links"])[:20],
        "stats": {
            "total_articles": len(articles_meta),
            "total_tags": len(tag_nodes),
            "total_concepts": len(concept_nodes),
            "total_nodes": G.number_of_nodes(),
            "total_edges": G.number_of_edges(),
            "avg_links_per_article": round(avg_links, 2),
        },
    }


# --- レポート生成 ---

def _md_table(headers: list[str], rows: list[list]) -> str:
    header_row = " | ".join(headers)
    sep_row = " | ".join(["---"] * len(headers))
    data_rows = "\n".join(" | ".join(str(c) for c in row) for row in rows)
    return f"| {header_row} |\n| {sep_row} |\n" + "\n".join(
        f"| {' | '.join(str(c) for c in row)} |" for row in rows
    )


def generate_report(result: dict, cfg: dict) -> str:
    """分析結果をMarkdown文字列にフォーマットする"""
    today = datetime.now().strftime("%Y-%m-%d")
    stats = result["stats"]

    lines = [
        "---",
        f"title: Graph Analysis Report {today}",
        "tags: [_analysis, graph, vault-stats]",
        f"generated: {today}",
        "---",
        "",
        f"# 知識グラフ分析レポート {today}",
        "",
        "## 総統計",
        "",
        f"| 指標 | 値 |",
        f"| --- | --- |",
        f"| 記事数 | {stats['total_articles']} |",
        f"| タグ種類数 | {stats['total_tags']} |",
        f"| 概念ノード数 | {stats['total_concepts']} |",
        f"| グラフノード総数 | {stats['total_nodes']} |",
        f"| グラフエッジ総数 | {stats['total_edges']} |",
        f"| 平均リンク数/記事 | {stats['avg_links_per_article']} |",
        "",
        "## タグ使用頻度ランキング（Top 30）",
        "",
    ]

    if result["tag_ranking"]:
        lines.append("| Rank | タグ | 記事数 |")
        lines.append("| --- | --- | --- |")
        for i, (tag, cnt) in enumerate(result["tag_ranking"], 1):
            lines.append(f"| {i} | {tag} | {cnt} |")
    else:
        lines.append("_タグなし_")

    lines += [
        "",
        "## 最多参照概念（Wikilinks Top 20）",
        "",
    ]

    if result["top_concepts"]:
        lines.append("| Rank | 概念 | 参照数 |")
        lines.append("| --- | --- | --- |")
        for i, (concept, deg) in enumerate(result["top_concepts"], 1):
            lines.append(f"| {i} | [[{concept}]] | {deg} |")
    else:
        lines.append("_Wikilinkなし_")

    lines += [
        "",
        "## カバレッジギャップ（Taxonomyで未使用のタグ）",
        "",
    ]

    if result["unused_taxonomy"]:
        lines.append(f"未使用タグ数: **{len(result['unused_taxonomy'])}**")
        lines.append("")
        for tag in result["unused_taxonomy"]:
            lines.append(f"- {tag}")
    else:
        lines.append("_すべてのTaxonomyタグが使用されています_")

    lines += [
        "",
        "## 孤立記事（リンク数 < 2、最大20件）",
        "",
    ]

    if result["isolated_articles"]:
        lines.append("| タイトル | リンク数 |")
        lines.append("| --- | --- |")
        for art in result["isolated_articles"]:
            title = art["title"]
            links = art["links"]
            lines.append(f"| {title} | {links} |")
    else:
        lines.append("_孤立記事なし_")

    lines.append("")
    return "\n".join(lines)


# --- メインエントリ ---

def run_analysis(cfg: dict):
    """分析を実行してVaultにレポートを保存する"""
    vault_path = Path(cfg["vault"]["path"])
    if not vault_path.exists():
        logger.error("Vault not found: %s", vault_path)
        return

    G, articles_meta = build_graph(vault_path)
    result = analyze(G, articles_meta, cfg)
    report_md = generate_report(result, cfg)

    # レポート保存先
    analysis_dir = vault_path / "_analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    report_path = analysis_dir / f"graph_report_{today}.md"
    report_path.write_text(report_md, encoding="utf-8")
    logger.info("Graph report saved: %s", report_path)

    # サマリをコンソール出力
    stats = result["stats"]
    print(f"\n=== 知識グラフ分析完了 ===")
    print(f"記事数         : {stats['total_articles']}")
    print(f"タグ種類数     : {stats['total_tags']}")
    print(f"概念ノード数   : {stats['total_concepts']}")
    print(f"平均リンク数   : {stats['avg_links_per_article']}")
    print(f"未使用タグ数   : {len(result['unused_taxonomy'])}")
    print(f"孤立記事数     : {len(result['isolated_articles'])}")
    print(f"レポート保存   : {report_path}")

    if result["tag_ranking"]:
        print(f"\nタグTOP5: {', '.join(f'{t}({c})' for t, c in result['tag_ranking'][:5])}")
    if result["top_concepts"]:
        print(f"概念TOP5: {', '.join(f'{c}({d})' for c, d in result['top_concepts'][:5])}")
