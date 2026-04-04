"""Obsidian Vault へのMarkdown書き込みモジュール"""
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

TYPE_TO_DIR = {
    "paper": "papers",
    "blog": "blogs",
    "notebook": "notebooks",
    "idea": "ideas",
}


def _slugify(text: str, max_len: int = 50) -> str:
    """タイトルをファイル名に使える文字列に変換"""
    # 英数字・日本語・ハイフン以外を削除
    text = re.sub(r"[^\w\u3040-\u30ff\u4e00-\u9fff\-]", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:max_len]


def write(article: dict, formatted_md: str, cfg: dict) -> Path | None:
    """整形済みMarkdownをVaultに保存してPathを返す。失敗時はNone"""
    vault_root = Path(cfg["vault"]["path"])
    article_type = article.get("type", "blog")

    # competition タイプは competitions/<comp_slug>/ に保存
    if article_type == "competition":
        comp_slug = article.get("comp_slug", "unknown")
        target_dir = vault_root / "competitions" / comp_slug
    else:
        subdir_key = TYPE_TO_DIR.get(article_type, "blogs")
        subdir_name = cfg["vault"].get(f"{subdir_key}_dir", subdir_key)
        target_dir = vault_root / subdir_name
    target_dir.mkdir(parents=True, exist_ok=True)

    date_str = article.get("published", "19700101").replace("-", "")[:8]
    slug = _slugify(article.get("title", "untitled"))
    filename = f"{date_str}_{slug}.md"
    filepath = target_dir / filename

    # 同名ファイルが既存の場合はスキップ（上書きしない）
    if filepath.exists():
        logger.debug("Already exists, skip: %s", filepath.name)
        return filepath

    try:
        filepath.write_text(formatted_md, encoding="utf-8")
        logger.info("Saved: %s", filepath.relative_to(vault_root))
        return filepath
    except OSError as e:
        logger.error("Write failed [%s]: %s", filename, e)
        return None
