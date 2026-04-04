#!/usr/bin/env python3
"""
SessionEnd hook: 編集されたファイルを検出し、関連プロジェクトの SESSION_NOTES.md に
セッション活動ログを追記する。
"""
import json
import sys
from pathlib import Path
from datetime import datetime


WORKSPACE = Path("C:/workspace/ai-os")


def normalize_path(fp: str) -> Path:
    """transcriptのUnix形式パス(/c/workspace/...)をWindowsパスに変換する。"""
    if fp.startswith("/c/"):
        fp = "C:/" + fp[3:]
    return Path(fp)


def parse_transcript(transcript_path: str) -> tuple[set, list]:
    """transcript JSONL を解析して編集ファイルとBashコマンドを返す。"""
    edited_files: set[str] = set()
    commands: list[str] = []

    p = Path(transcript_path)
    if not p.exists():
        return edited_files, commands

    try:
        with open(p, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg = entry.get("message", {})
                if not isinstance(msg, dict):
                    continue

                for content in msg.get("content", []):
                    if not isinstance(content, dict):
                        continue
                    if content.get("type") != "tool_use":
                        continue

                    name = content.get("name", "")
                    inp = content.get("input", {}) or {}

                    if name in ("Write", "Edit"):
                        fp = inp.get("file_path", "")
                        if fp:
                            edited_files.add(str(normalize_path(fp)))
                    elif name == "Bash":
                        cmd = (inp.get("command") or inp.get("description") or "").strip()
                        if cmd:
                            commands.append(cmd[:120])
    except Exception as e:
        print(f"[sync-session-notes] transcript parse error: {e}", file=sys.stderr)

    return edited_files, commands


def find_project_session_notes(edited_files: set) -> list[Path]:
    """編集ファイルのパスからプロジェクトの SESSION_NOTES.md を特定する。"""
    found: set[Path] = set()

    for fp in edited_files:
        p = Path(fp)
        for parent in p.parents:
            if parent == WORKSPACE:
                break
            try:
                parent.relative_to(WORKSPACE)
            except ValueError:
                break
            sn = parent / "SESSION_NOTES.md"
            if sn.exists():
                found.add(sn)
                break

    return list(found)


def build_entry(edited_files: set, commands: list) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"\n---\n", f"## Session Log {now}\n"]

    if edited_files:
        lines.append("\n**編集ファイル:**\n")
        for fp in sorted(edited_files)[:15]:
            try:
                rel = Path(fp).relative_to(WORKSPACE)
                lines.append(f"- {rel}\n")
            except ValueError:
                lines.append(f"- {fp}\n")

    if commands:
        lines.append("\n**実行コマンド（抜粋）:**\n")
        seen = set()
        count = 0
        for cmd in commands:
            if cmd not in seen and count < 5:
                lines.append(f"- `{cmd}`\n")
                seen.add(cmd)
                count += 1

    return "".join(lines)


def main():
    raw = sys.stdin.read().strip()
    try:
        data = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        data = {}

    transcript_path = data.get("transcript_path", "")
    if not transcript_path:
        print("[sync-session-notes] no transcript_path provided, skipping.")
        return
    edited_files, commands = parse_transcript(transcript_path)

    session_notes_list = find_project_session_notes(edited_files)

    if not session_notes_list:
        print("[sync-session-notes] no project SESSION_NOTES detected, skipping.")
        return

    entry = build_entry(edited_files, commands)

    for sn_path in session_notes_list:
        try:
            with open(sn_path, "a", encoding="utf-8") as f:
                f.write(entry)
            print(f"[sync-session-notes] appended to: {sn_path}")
        except Exception as e:
            print(f"[sync-session-notes] error writing {sn_path}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
