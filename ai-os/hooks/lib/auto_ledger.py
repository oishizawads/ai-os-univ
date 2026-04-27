#!/usr/bin/env python3
"""
PostToolUse hook: result.md への書き込みを検知し、
最寄りの experiment_ledger.csv に行を自動追記する。
"""
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def normalize_path(raw: str) -> Path:
    if raw.startswith("/c/"):
        raw = "C:/" + raw[3:]
    return Path(raw)


def find_ledger(start: Path) -> Path | None:
    for parent in [start.parent, *start.parents]:
        ledger = parent / "experiment_ledger.csv"
        if ledger.exists():
            return ledger
        if (parent / "CLAUDE.md").exists():
            return parent / "experiment_ledger.csv"
    return None


def extract_metrics(content: str) -> dict:
    """result.md から CV / LB スコアを正規表現で抽出する。"""
    cv, lb = "", ""

    cv_match = re.search(r"(?:cv|cross.?val)[^\d]*?([\d]+\.[\d]+)", content, re.IGNORECASE)
    if cv_match:
        cv = cv_match.group(1)

    lb_match = re.search(r"(?:lb|public\s*lb|leaderboard)[^\d]*?([\d]+\.[\d]+)", content, re.IGNORECASE)
    if lb_match:
        lb = lb_match.group(1)

    return {"cv": cv, "lb": lb}


def extract_note(content: str) -> str:
    """## Summary / ## Note / ## Result セクションの先頭1行を取得する。"""
    for section in ["Summary", "Note", "Result", "結果", "まとめ"]:
        m = re.search(rf"##\s+{section}\s*\n(.*)", content, re.IGNORECASE)
        if m:
            return m.group(1).strip()[:120]
    return ""


def main():
    raw = sys.stdin.read().strip()
    try:
        payload = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return

    if payload.get("tool_name") not in ("Write", "Edit"):
        return

    raw_path = (payload.get("tool_input") or {}).get("file_path", "")
    if not raw_path:
        return

    file_path = normalize_path(raw_path)
    if file_path.name != "result.md":
        return

    ledger = find_ledger(file_path)
    if ledger is None:
        return

    content = file_path.read_text(encoding="utf-8", errors="ignore") if file_path.exists() else ""
    metrics = extract_metrics(content)
    note = extract_note(content)

    try:
        rel = file_path.relative_to(ledger.parent)
        experiment_name = str(rel.parent).replace("\\", "/")
    except ValueError:
        experiment_name = str(file_path.parent)

    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "experiment": experiment_name,
        "cv": metrics["cv"],
        "lb": metrics["lb"],
        "note": note,
        "result_md": str(file_path).replace("\\", "/"),
    }

    write_header = not ledger.exists() or ledger.stat().st_size == 0
    with open(ledger, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    print(f"[auto-ledger] recorded: {experiment_name} | cv={metrics['cv']} lb={metrics['lb']}")


if __name__ == "__main__":
    main()
