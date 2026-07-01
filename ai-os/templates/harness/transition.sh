#!/usr/bin/env bash
# Issueのラベルを次のステータスに遷移させる
# 使い方: bash transition.sh <issue#> <next-status> [owner/repo]
# 例: bash transition.sh 42 design OugaIshizawa/near-infrared-challenge

set -e

ISSUE=${1:?"使い方: bash transition.sh <issue#> <next-status> [owner/repo]"}
NEXT=${2:?"使い方: bash transition.sh <issue#> <next-status> [owner/repo]"}
REPO=${3:-$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)}

if [ -z "$REPO" ]; then
  echo "エラー: リポジトリを特定できません。3番目の引数で指定してください"
  exit 1
fi

# ステータスラベルの定義
STATUS_LABELS=(
  "status:requirement"
  "status:design"
  "status:ready"
  "status:implementing"
  "status:review"
  "status:merged"
  "status:blocked"
)

# エージェントラベルのマッピング
declare -A AGENT_MAP
AGENT_MAP["requirement"]="agent:claude"
AGENT_MAP["design"]="agent:claude"
AGENT_MAP["ready"]="agent:codex"
AGENT_MAP["implementing"]="agent:codex"
AGENT_MAP["review"]="agent:claude"
AGENT_MAP["merged"]="agent:claude"
AGENT_MAP["blocked"]="agent:human"

echo "Issue #$ISSUE を status:$NEXT に遷移します ($REPO)"

# 現在付いているラベルを取得
CURRENT_LABELS=$(gh issue view "$ISSUE" --repo "$REPO" --json labels -q '.labels[].name' 2>/dev/null)

# 既存のステータスラベルを削除（付いているものだけ）
for label in "${STATUS_LABELS[@]}"; do
  if echo "$CURRENT_LABELS" | grep -qx "$label"; then
    gh issue edit "$ISSUE" --remove-label "$label" --repo "$REPO" >/dev/null 2>&1 || true
  fi
done

# 既存のエージェントラベルを削除（付いているものだけ）
for agent in "agent:claude" "agent:codex" "agent:human"; do
  if echo "$CURRENT_LABELS" | grep -qx "$agent"; then
    gh issue edit "$ISSUE" --remove-label "$agent" --repo "$REPO" >/dev/null 2>&1 || true
  fi
done

# 新しいラベルを付与
gh issue edit "$ISSUE" --add-label "status:$NEXT" --repo "$REPO"

if [ -n "${AGENT_MAP[$NEXT]}" ]; then
  gh issue edit "$ISSUE" --add-label "${AGENT_MAP[$NEXT]}" --repo "$REPO"
fi

echo "完了: Issue #$ISSUE → status:$NEXT, ${AGENT_MAP[$NEXT]:-}"
