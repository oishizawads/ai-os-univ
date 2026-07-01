#!/usr/bin/env python3
"""AI 生成コードの検証スクリプト

AI が生成したコードに対して、ローカルで即座に検証を実行する。
pre-commit フックまたは CI パイプラインから呼び出されることを想定。
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """コマンドを実行し、結果を返す"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            print(f"✓ {description} passed")
            return True
        else:
            print(f"✗ {description} failed")
            if result.stdout:
                print(f"stdout:\n{result.stdout}")
            if result.stderr:
                print(f"stderr:\n{result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ {description} timed out")
        return False
    except Exception as e:
        print(f"✗ {description} error: {e}")
        return False


def stage1_lint(target: str) -> bool:
    """Stage 1: Lint & Format"""
    print("\n### Stage 1: Lint & Format ###")

    results = []
    results.append(run_command(
        ["uv", "run", "ruff", "check", target],
        "Ruff lint check"
    ))
    results.append(run_command(
        ["uv", "run", "ruff", "format", "--check", target],
        "Ruff format check"
    ))

    return all(results)


def stage2_type_check(target: str) -> bool:
    """Stage 2: Type Check"""
    print("\n### Stage 2: Type Check ###")

    return run_command(
        ["uv", "run", "mypy", target],
        "MyPy type check"
    )


def stage3_tests(test_dir: str, min_coverage: float = 90.0) -> bool:
    """Stage 3: Run Tests"""
    print("\n### Stage 3: Run Tests ###")

    cmd = [
        "uv", "run", "pytest", test_dir, "-v",
        f"--cov=src",
        f"--cov-fail-under={min_coverage}",
        "--cov-report=term-missing"
    ]

    return run_command(cmd, "Pytest with coverage")


def stage4_security(target: str) -> bool:
    """Stage 4: Security Scan"""
    print("\n### Stage 4: Security Scan ###")

    results = []
    results.append(run_command(
        ["uv", "run", "semgrep", "--config", "auto", target],
        "Semgrep security scan"
    ))
    results.append(run_command(
        ["uv", "run", "gitleaks", "detect", "--source", "."],
        "Gitleaks secret scan"
    ))

    return all(results)


def main():
    parser = argparse.ArgumentParser(description="AI 生成コード検証スクリプト")
    parser.add_argument("--target", default="src/", help="検証対象ディレクトリ")
    parser.add_argument("--test-dir", default="tests/", help="テストディレクトリ")
    parser.add_argument("--min-coverage", type=float, default=90.0, help="最低カバレッジ")
    parser.add_argument("--stage", choices=["1", "2", "3", "4", "all"], default="all",
                        help="実行するステージ")

    args = parser.parse_args()

    print("AI Verification Pipeline")
    print(f"Target: {args.target}")
    print(f"Test Dir: {args.test_dir}")
    print(f"Min Coverage: {args.min_coverage}%")

    results = {}

    if args.stage in ["1", "all"]:
        results["lint"] = stage1_lint(args.target)

    if args.stage in ["2", "all"]:
        results["type_check"] = stage2_type_check(args.target)

    if args.stage in ["3", "all"]:
        results["tests"] = stage3_tests(args.test_dir, args.min_coverage)

    if args.stage in ["4", "all"]:
        results["security"] = stage4_security(args.target)

    # 結果サマリー
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)

    all_passed = True
    for stage, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{stage}: {status}")
        if not passed:
            all_passed = False

    print("="*60)

    if all_passed:
        print("All verification stages passed!")
        sys.exit(0)
    else:
        print("Some verification stages failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
