#!/usr/bin/env bash
# 対象リポジトリにharness用ラベルを一括投入する
# 使い方: bash setup-labels.sh <owner/repo>
# 例: bash setup-labels.sh OugaIshizawa/near-infrared-challenge

set -e

REPO=${1:?"使い方: bash setup-labels.sh <owner/repo>"}

echo "ラベルを投入します: $REPO"

create_label() {
  local name=$1
  local color=$2
  local desc=$3
  # 既存なら更新、なければ作成
  gh label create "$name" --color "$color" --description "$desc" --repo "$REPO" --force
}

# status
create_label "status:requirement"   "0075ca" "要件定義中"
create_label "status:design"        "cfd3d7" "設計中"
create_label "status:ready"         "e4e669" "実装待ち"
create_label "status:implementing"  "d93f0b" "実装中"
create_label "status:review"        "0e8a16" "レビュー中"
create_label "status:merged"        "6f42c1" "完了"
create_label "status:blocked"       "b60205" "ブロック中"

# type
create_label "type:feature"    "a2eeef" "新機能・改善"
create_label "type:bug"        "d73a4a" "バグ修正"
create_label "type:refactor"   "e99695" "リファクタリング"
create_label "type:experiment" "f9d0c4" "実験・PoC"
create_label "type:docs"       "fef2c0" "ドキュメント"

# agent
create_label "agent:claude" "0052cc" "Claudeが担当中"
create_label "agent:codex"  "006b75" "Codexが担当中"
create_label "agent:human"  "e4e669" "人間の判断待ち"

# priority
create_label "priority:high"   "b60205" "優先度高"
create_label "priority:medium" "fbca04" "優先度中"
create_label "priority:low"    "0075ca" "優先度低"

echo "完了: $(gh label list --repo "$REPO" | wc -l) 個のラベルが存在します"
