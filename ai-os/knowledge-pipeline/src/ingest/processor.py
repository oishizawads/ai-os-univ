"""raw/ の新規mdファイルを処理してインデックス更新 + ChromaDB登録"""
import logging
import os
import re
from datetime import datetime
from pathlib import Path

import anthropic

from .index import get_indexed_files, append_entry

logger = logging.getLogger(__name__)

INGEST_SYSTEM_PROMPT = """あなたはドキュメントを分析して、タイトル・要約・タグを抽出するアシスタントです。

以下のフォーマットで出力してください。他の文章は一切出力しないこと。

title: <記事のタイトル（なければ内容から推測）>
summary: <1行要約（50文字以内、日本語）>
tags: <タグ1>, <タグ2>, <タグ3>
"""


def _build_prompt(content: str, taxonomy: list[str]) -> str:
    taxonomy_str = ", ".join(taxonomy[:50])
    return f"""以下のドキュメントを分析してください。

tagsは以下のtaxonomyから最大3つ選んでください:
{taxonomy_str}

---
{content[:8000]}
"""


def _extract_url_from_frontmatter(content: str) -> str:
    """ファイルのフロントマターからURLを抽出する"""
    if not content.startswith("---"):
        return ""
    end = content.find("\n---", 3)
    if end == -1:
        return ""
    for line in content[3:end].splitlines():
        m = re.match(r"^url:\s*(.+)", line.strip())
        if m:
            return m.group(1).strip().strip('"\'')
    return ""


def _parse_response(text: str) -> dict:
    result = {"title": "", "summary": "", "tags": []}
    for line in text.strip().splitlines():
        if line.startswith("title:"):
            result["title"] = line.split(":", 1)[1].strip()
        elif line.startswith("summary:"):
            result["summary"] = line.split(":", 1)[1].strip()
        elif line.startswith("tags:"):
            tags_raw = line.split(":", 1)[1].strip()
            result["tags"] = [t.strip() for t in tags_raw.split(",") if t.strip()]
    return result


def process_new_files(cfg: dict) -> int:
    """raw/ の未処理ファイルを処理して _INDEX.md 更新 + ChromaDB 登録。処理件数を返す"""
    vault_cfg = cfg["vault"]
    vault_root = Path(vault_cfg["path"])
    raw_dir = vault_root / vault_cfg.get("raw_dir", "raw")

    if not raw_dir.exists():
        logger.warning("raw/ ディレクトリが存在しません: %s", raw_dir)
        return 0

    indexed = get_indexed_files(vault_cfg)
    taxonomy = cfg.get("tags", {}).get("taxonomy", [])

    candidates = [
        p for p in raw_dir.glob("*.md")
        if p.name != "_INDEX.md" and p.stem not in indexed
    ]

    if not candidates:
        logger.info("新規ファイルなし")
        return 0

    logger.info("新規ファイル %d 件を処理します", len(candidates))

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    claude_cfg = cfg["claude"]
    today = datetime.now().strftime("%Y-%m-%d")

    # Embedder は1回だけ初期化（モデルロードが重いため）
    embedder = None
    try:
        from src.rag.embedder import Embedder
        embedder = Embedder(cfg)
    except Exception as e:
        logger.warning("Embedder初期化失敗（embedding はスキップ）: %s", e)

    processed = 0
    for path in sorted(candidates):
        logger.info("処理中: %s", path.name)
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error("読み込み失敗: %s — %s", path.name, e)
            continue

        # Claude API で要約・タグ生成
        try:
            resp = client.messages.create(
                model=claude_cfg["model"],
                max_tokens=300,
                temperature=0.1,
                system=INGEST_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": _build_prompt(content, taxonomy)}],
            )
            parsed = _parse_response(resp.content[0].text)
        except Exception as e:
            logger.error("Claude API失敗: %s — %s", path.name, e)
            continue

        title = parsed["title"] or path.stem
        summary = parsed["summary"] or ""
        tags = parsed["tags"]

        # _INDEX.md に追記
        append_entry(vault_cfg, path.name, title, summary, tags, today)
        logger.info("インデックス登録: %s | %s", path.name, summary[:40])

        # ChromaDB に登録
        if embedder:
            try:
                article_meta = {
                    "title": title,
                    "type": "raw",
                    "published": today,
                    "url": _extract_url_from_frontmatter(content),
                    "tags": tags,
                }
                n = embedder.embed_file(path, article_meta)
                logger.info("Embedded %d entries: %s", n, path.name)
            except Exception as e:
                logger.warning("Embedding失敗（非致命的）: %s — %s", path.name, e)

        processed += 1

    logger.info("=== ingest完了: %d / %d 件 ===", processed, len(candidates))
    return processed
