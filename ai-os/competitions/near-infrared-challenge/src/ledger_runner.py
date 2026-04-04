from __future__ import annotations

import argparse
import csv
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", required=True, help="Path to ledger csv")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--only", nargs="*", default=None)
    return parser.parse_args()


def read_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as fp:
        return list(csv.DictReader(fp))


def write_rows(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def should_run(row: dict, only: set[str] | None, resume: bool) -> bool:
    enabled = row.get("enabled", "").strip().upper() == "TRUE"
    if not enabled:
        return False
    if only is not None and row["experiment_id"] not in only:
        return False
    if resume and row.get("status", "") == "completed":
        return False
    return row.get("command", "").strip() != ""


def update_report(ledger_path: Path, rows: list[dict]) -> None:
    summary_path = ledger_path.with_name("summary.md")
    completed = [r for r in rows if r.get("status") == "completed"]
    completed.sort(key=lambda r: (int(r.get("priority", "999")), r["experiment_id"]))
    lines = [
        f"# {ledger_path.stem}",
        "",
        f"- updated_at_utc: {datetime.now(timezone.utc).isoformat()}",
        f"- completed: {len(completed)}",
        "",
        "| experiment_id | priority | theme | status | exit_code | last_run_utc |",
        "| --- | ---: | --- | --- | ---: | --- |",
    ]
    for row in completed:
        lines.append(
            f"| {row['experiment_id']} | {row.get('priority','')} | {row.get('theme','')} | "
            f"{row.get('status','')} | {row.get('last_exit_code','')} | {row.get('last_run_utc','')} |"
        )
    summary_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    ledger_path = Path(args.ledger).resolve()
    rows = read_rows(ledger_path)
    fieldnames = list(rows[0].keys()) if rows else []
    extra_fields = ["last_run_utc", "last_exit_code", "last_stdout_tail", "last_stderr_tail"]
    for field in extra_fields:
        if field not in fieldnames:
            fieldnames.append(field)
            for row in rows:
                row[field] = row.get(field, "")

    only = set(args.only) if args.only else None
    runnable = [row for row in rows if should_run(row, only, args.resume)]
    runnable.sort(key=lambda r: (int(r.get("priority", "999")), r["experiment_id"]))
    if args.limit is not None:
        runnable = runnable[: args.limit]

    for target in runnable:
        target["status"] = "running"
        write_rows(ledger_path, rows, fieldnames)
        workdir = target.get("workdir", "").strip() or str(ledger_path.parent.parent)
        completed = subprocess.run(
            target["command"],
            cwd=workdir,
            shell=True,
            capture_output=True,
            text=True,
        )
        target["last_run_utc"] = datetime.now(timezone.utc).isoformat()
        target["last_exit_code"] = str(completed.returncode)
        target["last_stdout_tail"] = completed.stdout[-500:]
        target["last_stderr_tail"] = completed.stderr[-500:]
        target["status"] = "completed" if completed.returncode == 0 else "failed"
        write_rows(ledger_path, rows, fieldnames)
        update_report(ledger_path, rows)


if __name__ == "__main__":
    main()
