#!/usr/bin/env python3
"""
Session 開始時コンテキストローダー。
Usage: python session_start.py [project_dir]

SESSION_NOTES.md / .steering/ / experiment_ledger.csv / DECISION_LOG.md を
読んで、現在地を素早く把握するためのサマリを表示する。
"""
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
SEP = "=" * 62


def read_tail(path: Path, max_lines: int = 40) -> str:
    if not path.exists():
        return "(not found)"
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    recent = lines[-max_lines:] if len(lines) > max_lines else lines
    prefix = f"(showing last {max_lines} of {len(lines)} lines)\n" if len(lines) > max_lines else ""
    return prefix + "\n".join(recent)


def read_head(path: Path, max_lines: int = 25) -> str:
    if not path.exists():
        return "(not found)"
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    body = lines[:max_lines]
    suffix = f"\n... (+{len(lines)-max_lines} lines)" if len(lines) > max_lines else ""
    return "\n".join(body) + suffix


def latest_steering(project_dir: Path) -> str:
    d = project_dir / ".steering"
    if not d.exists():
        return "(no .steering/)"
    files = sorted(d.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return "(empty)"
    f = files[0]
    return f"[{f.name}]\n" + read_head(f, max_lines=20)


def latest_ledger(project_dir: Path, n: int = 8) -> str:
    ledger = project_dir / "experiment_ledger.csv"
    if not ledger.exists():
        return "(no experiment_ledger.csv)"
    lines = ledger.read_text(encoding="utf-8", errors="ignore").splitlines()
    if len(lines) <= 1:
        return "(ledger is empty)"
    header = lines[0]
    rows = lines[1:][-n:]
    return header + "\n" + "\n".join(rows)


def decision_log_tail(project_dir: Path) -> str:
    log = project_dir / "DECISION_LOG.md"
    return read_tail(log, max_lines=20)


def section(title: str, content: str) -> str:
    return f"\n## {title}\n{content}\n"


def main():
    project_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else WORKSPACE
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    print(f"\n{SEP}")
    print(f"  SESSION START  {now}")
    print(f"  Project: {project_dir}")
    print(SEP)

    print(section("SESSION_NOTES.md (tail)", read_tail(project_dir / "SESSION_NOTES.md")))
    print(section(".steering/ (latest)", latest_steering(project_dir)))
    print(section("experiment_ledger.csv (last 8)", latest_ledger(project_dir)))
    print(section("DECISION_LOG.md (tail)", decision_log_tail(project_dir)))

    print(f"{SEP}")
    print("  Context loaded. Go.\n")
    print(SEP)


if __name__ == "__main__":
    main()
