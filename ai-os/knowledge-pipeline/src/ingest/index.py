"""raw/_INDEX.md の読み書き管理"""
import re
from datetime import datetime
from pathlib import Path


INDEX_HEADER = """---
title: Raw Document Index
updated: {date}
---

# Raw Index

| ファイル | タイトル | 要約 | タグ | 追加日 |
|---------|---------|-----|-----|-------|
"""


def get_index_path(vault_cfg: dict) -> Path:
    vault_root = Path(vault_cfg["path"])
    raw_dir = vault_root / vault_cfg.get("raw_dir", "raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    return raw_dir / "_INDEX.md"


def get_indexed_files(vault_cfg: dict) -> set[str]:
    """_INDEX.md に登録済みのファイル名セットを返す"""
    index_path = get_index_path(vault_cfg)
    if not index_path.exists():
        return set()

    text = index_path.read_text(encoding="utf-8")
    # | [[filename]] | ... の行からファイル名を抽出
    names = re.findall(r"\|\s*\[\[([^\]]+)\]\]", text)
    return set(names)


def append_entry(vault_cfg: dict, filename: str, title: str, summary: str, tags: list[str], date: str):
    """_INDEX.md に1エントリ追記する"""
    index_path = get_index_path(vault_cfg)

    if not index_path.exists():
        index_path.write_text(INDEX_HEADER.format(date=date), encoding="utf-8")

    stem = Path(filename).stem
    tags_str = ", ".join(tags)
    row = f"| [[{stem}]] | {title} | {summary} | {tags_str} | {date} |\n"

    # updated日付を更新
    text = index_path.read_text(encoding="utf-8")
    text = re.sub(r"updated: .+", f"updated: {date}", text)
    text += row
    index_path.write_text(text, encoding="utf-8")
