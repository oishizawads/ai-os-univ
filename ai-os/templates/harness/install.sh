#!/usr/bin/env bash
# 任意のリポジトリにharnessテンプレートを展開する
# 使い方: bash install.sh <repo_local_path> <owner/repo> [--with-actions]
# 例: bash install.sh /c/workspace/near-infrared-challenge OugaIshizawa/near-infrared-challenge
# 例: bash install.sh /c/workspace/harness-test oishizawads/harness-test --with-actions

set -e

REPO_PATH=${1:?"使い方: bash install.sh <repo_local_path> <owner/repo> [--with-actions]"}
REPO_REMOTE=${2:?"使い方: bash install.sh <repo_local_path> <owner/repo> [--with-actions]"}
WITH_ACTIONS=false
if [[ "${3:-}" == "--with-actions" ]]; then
  WITH_ACTIONS=true
fi
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Harness テンプレートを展開します ==="
echo "対象ディレクトリ: $REPO_PATH"
echo "GitHub リポジトリ: $REPO_REMOTE"
echo ""

# .github/ISSUE_TEMPLATE/ を作成
mkdir -p "$REPO_PATH/.github/ISSUE_TEMPLATE"
cp "$SCRIPT_DIR/ISSUE_TEMPLATE/"*.md "$REPO_PATH/.github/ISSUE_TEMPLATE/"
echo "✓ Issueテンプレートをコピーしました"

# WORKFLOW.md をコピー
cp "$SCRIPT_DIR/WORKFLOW.md" "$REPO_PATH/.github/WORKFLOW.md"
echo "✓ WORKFLOW.md をコピーしました"

# RUNBOOK.md をコピー
cp "$SCRIPT_DIR/RUNBOOK.md" "$REPO_PATH/.github/RUNBOOK.md"
echo "✓ RUNBOOK.md をコピーしました"

# PRテンプレートをコピー
cp "$SCRIPT_DIR/PULL_REQUEST_TEMPLATE.md" "$REPO_PATH/.github/PULL_REQUEST_TEMPLATE.md"
echo "✓ PRテンプレートをコピーしました"

# prompts/ をコピー
mkdir -p "$REPO_PATH/.github/harness-prompts"
cp "$SCRIPT_DIR/prompts/"*.md "$REPO_PATH/.github/harness-prompts/"
echo "✓ prompts/ をコピーしました"

# transition.sh をコピー
cp "$SCRIPT_DIR/transition.sh" "$REPO_PATH/.github/transition.sh"
chmod +x "$REPO_PATH/.github/transition.sh"
echo "✓ transition.sh をコピーしました"

# ラベルを投入
bash "$SCRIPT_DIR/setup-labels.sh" "$REPO_REMOTE"
echo "✓ ラベルを投入しました"

# GitHub Actions ワークフローのコピー（オプション）
if [ "$WITH_ACTIONS" = true ]; then
  if [ ! -d "$SCRIPT_DIR/workflows" ]; then
    echo "⚠️  workflows/ ディレクトリが見つかりません。スキップします。"
  else
    mkdir -p "$REPO_PATH/.github/workflows"
    cp "$SCRIPT_DIR/workflows/"*.yml "$REPO_PATH/.github/workflows/"
    cp "$SCRIPT_DIR/SETUP_ACTIONS.md" "$REPO_PATH/.github/SETUP_ACTIONS.md"
    echo "✓ GitHub Actions ワークフローをコピーしました"
    echo "✓ SETUP_ACTIONS.md をコピーしました"
  fi
fi

echo ""
echo "=== 完了 ==="
echo "次のステップ:"
echo "  1. $REPO_PATH/.github/ をコミット・プッシュ"
echo "  2. GitHub の Issues > Labels でラベルを確認"
echo "  3. CHECKLIST.md を見ながら要求Issueを1つ作成してフローを試す"
if [ "$WITH_ACTIONS" = true ]; then
  echo ""
  echo "GitHub Actions セットアップ:"
  echo "  → $REPO_PATH/.github/SETUP_ACTIONS.md を参照"
fi
echo ""
echo "RUNBOOK: $REPO_PATH/.github/RUNBOOK.md"
echo "プロンプト集: $REPO_PATH/.github/harness-prompts/"
echo "ラベル遷移: bash $REPO_PATH/.github/transition.sh <issue#> <status>"
