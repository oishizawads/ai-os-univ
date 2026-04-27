#!/usr/bin/env python3
"""PreToolUse hook: 危険な Bash コマンドを検知してブロックする。exit 2 で Claude をブロック。"""
import json
import sys
import re

DANGEROUS_PATTERNS = [
    (r"(?<!['\"])\brm\s+-[rf]{1,2}f?\b", "rm -rf は破壊的です。本当に必要か確認してください"),
    (r"git\s+reset\s+--hard", "git reset --hard はコミットされていない変更を失います"),
    (r"git\s+push\s+--force(?!-with-lease)", "git push --force の代わりに --force-with-lease を使ってください"),
    (r"git\s+clean\s+-[fd]+", "git clean -f/d は追跡外ファイルを削除します"),
    (r"git\s+branch\s+-D\b", "git branch -D は強制削除です"),
    (r"\bDROP\s+TABLE\b", "DROP TABLE: 本番DB破壊の可能性があります"),
    (r"\bDROP\s+DATABASE\b", "DROP DATABASE: 危険なDDL操作です"),
    (r"\bTRUNCATE\s+TABLE\b", "TRUNCATE: 全データ削除です"),
    (r"chmod\s+-R\s+777", "chmod 777: セキュリティリスクがあります"),
    (r"dd\s+if=.*of=/dev/", "dd による直接書き込みは危険です"),
    (r"mkfs\b", "ファイルシステムのフォーマット操作です"),
    (r":\(\)\{[^}]+\|[^}]+&\}", "Fork bomb を検出しました"),
    (r"curl\b.*\|\s*(?:bash|sh)\b", "curl | bash は未検証コードを実行します"),
    (r"wget\b.*\|\s*(?:bash|sh)\b", "wget | bash は未検証コードを実行します"),
    (r"\bshred\b", "shred は復元不可能な削除です"),
    (r"format\s+[a-z]:", "ドライブのフォーマットは破壊的です"),
]

# echo/printf/cat の引数として渡されているだけの場合はスキップ
SAFE_PREFIXES = re.compile(r"^\s*(?:echo|printf|cat|grep|python|node)\b")

REVIEW_PATTERNS = [
    (r"git\s+push\b(?!.*--force)", "[review] git push: リモートへの反映です"),
    (r"pip\s+install\b", "[review] pip install: 依存関係が変わります"),
    (r"conda\s+(?:install|remove)\b", "[review] conda 環境を変更します"),
    (r"npm\s+(?:install|uninstall)\b", "[review] npm 依存関係を変更します"),
]


def main():
    raw = sys.stdin.read().strip()
    try:
        payload = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return

    if payload.get("tool_name") != "Bash":
        return

    command = (payload.get("tool_input") or {}).get("command", "")
    if not command:
        return

    # echo/printf 等への引数として渡されているだけのコマンドはスキップ
    if SAFE_PREFIXES.match(command):
        return

    for pattern, message in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            print(f"[guard] BLOCKED: {message}")
            print(f"[guard] コマンド: {command[:300]}")
            print("[guard] 本当に実行する場合はユーザーが明示的に許可してください。")
            sys.exit(2)

    for pattern, message in REVIEW_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            print(f"{message}: {command[:120]}")


if __name__ == "__main__":
    main()
