"""Wiki コンパイラ

_INDEX.md からコンセプトを抽出（主）+ [[wikilink]] スキャン（補助）でコンセプトページを生成。

フロー:
  1. raw/_INDEX.md を読んで Claude でコンセプトを抽出
  2. vault 全体の [[wikilink]] をスキャン（補助）
  3. 両者をマージして未生成コンセプトをリストアップ
  4. Claude API でコンセプトページを生成
  5. wiki/_INDEX.md を更新
"""
import hashlib
import json
import logging
import os
import re
from pathlib import Path

import anthropic
import yaml

logger = logging.getLogger(__name__)

CONCEPT_SYSTEM_PROMPT = """あなたはデータサイエンス・機械学習分野の技術百科事典の編集者です。
与えられたコンセプト名について、研究者・実務家が素早く参照できるWikiページを作成してください。

## 出力規則
- 日本語で記述する
- frontmatterは出力しない（呼び出し元が付与する）
- 関連する技術・手法は必ず [[概念名]] 形式でリンクする
- 実装・応用例を含める
- 簡潔かつ情報密度を高く保つ
"""

EXTRACT_CONCEPTS_SYSTEM = """あなたは知識ベースの編集者です。
ドキュメント一覧からWikiページを作るべきコンセプト（技術用語・概念・手法・アルゴリズム）を抽出してください。

出力フォーマット（1コンセプト1行）:
concept: <コンセプト名> | sources: <参照docのタイトル（カンマ区切り、最大3つ）>

条件:
- 具体的・専門的なコンセプトを優先する
- 「機械学習」「Python」「データ分析」のような一般的すぎる語は除外する
- 固有名詞（モデル名・手法名・ライブラリ名）を積極的に含める
- 日本語・英語どちらでも可
"""


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


def _scan_vault_for_wikilinks(dirs: list[Path]) -> dict[str, list[str]]:
    """vault を走査して [[wikilink]] → [記事タイトル] のマップを返す"""
    concept_map: dict[str, list[str]] = {}
    for d in dirs:
        if not d.exists():
            continue
        for md_path in sorted(d.rglob("*.md")):
            if md_path.name.startswith("_"):
                continue
            try:
                text = md_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            fm, body = _parse_frontmatter(text)
            title = fm.get("title") or md_path.stem
            for link in _extract_wikilinks(body):
                concept_map.setdefault(link, [])
                if title not in concept_map[link]:
                    concept_map[link].append(title)
    return concept_map


def _get_index_hash(index_path: Path) -> str:
    content = index_path.read_text(encoding="utf-8", errors="ignore")
    return hashlib.md5(content.encode()).hexdigest()


def _load_concept_cache(cache_path: Path) -> dict:
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_concept_cache(cache_path: Path, index_hash: str, concept_map: dict[str, list[str]]):
    cache_path.write_text(
        json.dumps({"hash": index_hash, "concepts": concept_map}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _extract_concepts_from_index(
    index_path: Path,
    existing_wiki: set[str],
    client: anthropic.Anthropic,
    claude_cfg: dict,
    force: bool = False,
) -> dict[str, list[str]]:
    """raw/_INDEX.md を読んで Claude でコンセプトを抽出する（ハッシュ変化時のみAPI呼び出し）"""
    if not index_path.exists():
        logger.info("_INDEX.md が存在しないためスキップ: %s", index_path)
        return {}

    content = index_path.read_text(encoding="utf-8")
    if len(content.strip()) < 100:
        return {}

    cache_path = index_path.parent / ".compile_cache.json"
    current_hash = _get_index_hash(index_path)

    if not force:
        cache = _load_concept_cache(cache_path)
        if cache.get("hash") == current_hash and cache.get("concepts"):
            logger.info("_INDEX.md 未変更 → キャッシュからコンセプトを読み込み（API呼び出しなし）")
            cached = cache["concepts"]
            return {c: v for c, v in cached.items() if c not in existing_wiki}

    try:
        resp = client.messages.create(
            model=claude_cfg["model"],
            max_tokens=1500,
            temperature=0.1,
            system=EXTRACT_CONCEPTS_SYSTEM,
            messages=[{
                "role": "user",
                "content": f"以下のドキュメント一覧からコンセプトを抽出してください:\n\n{content[:6000]}"
            }],
        )
        usage = resp.usage
        logger.info("概念抽出: input=%d output=%d tokens", usage.input_tokens, usage.output_tokens)
    except Exception as e:
        logger.error("概念抽出API失敗: %s", e)
        return {}

    concept_map: dict[str, list[str]] = {}
    for line in resp.content[0].text.splitlines():
        line = line.strip()
        if not line.startswith("concept:"):
            continue
        parts = line.split("|")
        concept = parts[0].split(":", 1)[1].strip()
        sources: list[str] = []
        if len(parts) > 1 and "sources:" in parts[1]:
            sources = [s.strip() for s in parts[1].split(":", 1)[1].split(",") if s.strip()]
        if concept:
            concept_map[concept] = sources

    logger.info("_INDEX.md から %d コンセプトを抽出", len(concept_map))
    _save_concept_cache(cache_path, current_hash, concept_map)
    return {c: v for c, v in concept_map.items() if c not in existing_wiki}


def _build_concept_prompt(concept: str, sources: list[str]) -> str:
    sources_str = "\n".join(f"- {s}" for s in sources[:10]) if sources else "（なし）"
    return f"""以下のコンセプトについてWikiページを作成してください。

## コンセプト名
{concept}

## このコンセプトが登場するドキュメント（参考）
{sources_str}

---

以下の構造で出力してください：

## 概要
（2〜3文で本質を述べる）

## 詳細
（手法・理論・アルゴリズムの詳細）

## 主な用途・応用
- （箇条書き）

## 実装メモ
（コード例・ライブラリ・注意点）

## 関連概念
（関連する技術・手法を [[概念名]] 形式で列挙）

## 参考文献・リンク
- （代表的な論文・ドキュメントURL）
"""


def _build_frontmatter(concept: str, source_count: int) -> str:
    return f"""---
title: "{concept}"
type: wiki
source_count: {source_count}
status: auto-generated
---
"""


def _get_concept_summary(wiki_dir: Path, concept: str) -> str:
    path = wiki_dir / f"{concept}.md"
    if not path.exists():
        return ""
    try:
        text = path.read_text(encoding="utf-8")
        fm, body = _parse_frontmatter(text)
        if fm.get("summary"):
            return str(fm["summary"])[:60]
        for line in body.splitlines():
            line = line.strip().lstrip("#").strip()
            if line and not line.startswith("---"):
                return line[:60]
    except Exception:
        pass
    return ""


def _update_wiki_index(wiki_dir: Path, all_concepts: list[str], concept_map: dict[str, list[str]]):
    """wiki/_INDEX.md を要約付きテーブルで更新"""
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")

    lines = [
        f"---\ntitle: Wiki Index\nupdated: {date_str}\n---\n\n",
        "# Wiki Index\n\n",
        f"総コンセプト数: {len(all_concepts)}\n\n",
        "| コンセプト | 要約 | 関連記事数 |\n",
        "|----------|-----|----------|\n",
    ]
    for c in sorted(all_concepts):
        summary = _get_concept_summary(wiki_dir, c)
        ref_count = len(concept_map.get(c, []))
        lines.append(f"| [[{c}]] | {summary} | {ref_count} |\n")

    (wiki_dir / "_INDEX.md").write_text("".join(lines), encoding="utf-8")
    logger.info("wiki/_INDEX.md updated: %d concepts", len(all_concepts))


def compile_wiki(cfg: dict, force: bool = False, batch_size: int = 10):
    vault_root = Path(cfg["vault"]["path"])
    wiki_dir = vault_root / cfg["vault"].get("wiki_dir", "wiki")
    wiki_dir.mkdir(parents=True, exist_ok=True)

    existing_wiki = {p.stem for p in wiki_dir.glob("*.md") if not p.stem.startswith("_")}

    claude_cfg = cfg["claude"]
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    # --- 主: _INDEX.md からコンセプト抽出 ---
    raw_index_path = vault_root / cfg["vault"].get("raw_dir", "raw") / "_INDEX.md"
    index_concepts = _extract_concepts_from_index(raw_index_path, existing_wiki, client, claude_cfg, force=force)

    # --- 補助: [[wikilink]] スキャン ---
    scan_dirs = [
        vault_root / cfg["vault"].get("raw_dir", "raw"),
        vault_root / cfg["vault"].get("inbox_dir", "inbox"),
        vault_root / cfg["vault"].get("blogs_dir", "blogs"),
        vault_root / cfg["vault"].get("papers_dir", "papers"),
        vault_root / cfg["vault"].get("notebooks_dir", "notebooks"),
    ]
    wikilink_concepts = _scan_vault_for_wikilinks(scan_dirs)
    logger.info("[[wikilink]] から %d コンセプトを検出", len(wikilink_concepts))

    # --- マージ ---
    concept_map: dict[str, list[str]] = {}
    for c, sources in index_concepts.items():
        concept_map[c] = sources
    for c, sources in wikilink_concepts.items():
        if c not in concept_map:
            concept_map[c] = sources
        else:
            # 両方にある場合はsourcesをマージ
            existing = set(concept_map[c])
            concept_map[c] += [s for s in sources if s not in existing]

    logger.info("合計コンセプト候補: %d", len(concept_map))

    # --- 未生成のコンセプトを抽出 ---
    pending = [c for c in sorted(concept_map) if force or c not in existing_wiki]
    logger.info("生成対象: %d / %d", len(pending), len(concept_map))

    if not pending:
        logger.info("全コンセプトページが最新です。")
        all_concepts = list(existing_wiki)
        _update_wiki_index(wiki_dir, all_concepts, concept_map)
        return

    # --- コンセプトページ生成 ---
    generated = 0
    for concept in pending[:batch_size]:
        sources = concept_map[concept]
        prompt = _build_concept_prompt(concept, sources)

        try:
            resp = client.messages.create(
                model=claude_cfg["model"],
                max_tokens=claude_cfg["max_tokens"],
                temperature=0.3,
                system=CONCEPT_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            body = resp.content[0].text
            usage = resp.usage
            logger.info("Wiki [%s]: input=%d output=%d tokens", concept, usage.input_tokens, usage.output_tokens)
        except anthropic.APIError as e:
            logger.error("Claude API error [%s]: %s", concept, e)
            continue

        fm = _build_frontmatter(concept, len(sources))
        (wiki_dir / f"{concept}.md").write_text(fm + "\n" + body, encoding="utf-8")
        generated += 1

    logger.info("生成完了: %d ページ", generated)
    if len(pending) > batch_size:
        logger.info("残り %d ページ。再度 --compile を実行してください", len(pending) - batch_size)

    # --- wiki/_INDEX.md 更新 ---
    all_concepts = [p.stem for p in wiki_dir.glob("*.md") if not p.stem.startswith("_")]
    _update_wiki_index(wiki_dir, all_concepts, concept_map)
