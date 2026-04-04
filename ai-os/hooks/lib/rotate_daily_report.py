#!/usr/bin/env python3
"""
SessionEnd hook: 各プロジェクトの daily/weekly/monthly レポートを自動生成する。
"""
from pathlib import Path
from datetime import datetime, timedelta


WORKSPACE = Path("C:/workspace/ai-os")

DAILY_TEMPLATE = """\
# Daily Report - {date}

## Done
-

## Today's Focus
-

## Risks
-

## Next
1.
"""

WEEKLY_TEMPLATE = """\
# Weekly Report - {year}-W{week:02d} ({date_range})

## Highlight
-

## Done
-

## Carry Over
-

## Risks / Blockers
-

## Next Week Focus
1.
"""

MONTHLY_TEMPLATE = """\
# Monthly Report - {year}-{month:02d}

## Theme
-

## Achievements
-

## Metrics / Results
-

## Lessons Learned
-

## Next Month Goals
1.
"""


def discover_projects() -> list[Path]:
    roots = []

    # competitions/ 直下
    comp_dir = WORKSPACE / "competitions"
    if comp_dir.exists():
        roots.extend(p for p in comp_dir.iterdir() if p.is_dir())

    # work/ 以下（深さ2まで）
    work_dir = WORKSPACE / "work"
    if work_dir.exists():
        for p in work_dir.iterdir():
            if p.is_dir():
                roots.append(p)
                roots.extend(c for c in p.iterdir() if c.is_dir())

    # ai-os
    roots.append(WORKSPACE / "ai-os")

    return roots


def ensure_daily(root: Path, date_str: str) -> None:
    daily_dir = root / "daily_reports"
    if not daily_dir.exists():
        return
    path = daily_dir / f"{date_str}.md"
    if path.exists():
        return
    path.write_text(DAILY_TEMPLATE.format(date=date_str), encoding="utf-8")
    print(f"[rotate-daily-report] created: {path}")


def ensure_weekly(root: Path, now: datetime) -> None:
    if now.weekday() != 0:
        return
    weekly_dir = root / "weekly_reports"
    if not weekly_dir.exists():
        return
    year, week, _ = now.isocalendar()
    monday = now
    sunday = monday + timedelta(days=6)
    date_range = f"{monday.strftime('%m/%d')} - {sunday.strftime('%m/%d')}"
    path = weekly_dir / f"{year}-W{week:02d}.md"
    if path.exists():
        return
    content = WEEKLY_TEMPLATE.format(year=year, week=week, date_range=date_range)
    path.write_text(content, encoding="utf-8")
    print(f"[rotate-daily-report] created: {path}")


def ensure_monthly(root: Path, now: datetime) -> None:
    if now.day != 1:
        return
    monthly_dir = root / "monthly_reports"
    if not monthly_dir.exists():
        return
    path = monthly_dir / f"{now.strftime('%Y-%m')}.md"
    if path.exists():
        return
    content = MONTHLY_TEMPLATE.format(year=now.year, month=now.month)
    path.write_text(content, encoding="utf-8")
    print(f"[rotate-daily-report] created: {path}")


def main():
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    for root in discover_projects():
        if not root.exists():
            continue
        try:
            ensure_daily(root, date_str)
            ensure_weekly(root, now)
            ensure_monthly(root, now)
        except Exception as e:
            print(f"[rotate-daily-report] error in {root}: {e}")

    print(f"[rotate-daily-report] done for {date_str}")


if __name__ == "__main__":
    main()
