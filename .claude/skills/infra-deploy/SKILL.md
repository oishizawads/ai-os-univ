---
name: infra-deploy
description: ホスティング/デプロイ/再現環境の正典（オンデマンド・委譲前提）。クライアントデモを安全に動かす最小構成を選び、重い設定はCodexへ委譲。
---

# Infra / Deploy

## Mission
作ったものを「人が触れる場所」に出す層。クライアントデモを最小コスト・最小リスクで動かす。インフラ専業を目指さず、選定と安全確認を担う。

## Rules
- **最小構成を選ぶ**: デモ共有なら Streamlit Community Cloud / Hugging Face Spaces / Render 等の手軽な順から。常時本番が要るまで重いクラウド構成にしない。
- **再現環境を固定**: 依存を `requirements.txt` / `uv` lock / Docker で固定（[[python-ops]]）。「自分の環境でだけ動く」を出さない。
- **秘密情報を環境変数に**: APIキー・認証情報はコードに埋めずenv/secretへ。**コミットしない**（[[safe-data-handling]]）。`.gitignore` を確認。
- **データの扱い**: クライアントデータをホスティング先に置く前に、置いていいデータか・PIIはないかを確認。ダミー/仮データで出せるなら出す（MTJの仮データ明示の流儀）。
- **重い設定は委譲**: Dockerfile・CI/CD・クラウド構成は仕様を渡して Codex/OpenCode に書かせ、自分はレビュー。

## オンデマンド参照（任意・要vet）
- `akin-ozer/cc-devops-skills`（Apache-2.0）: Dockerfile / GitHub Actions / GitLab CI 等の generator+validator（ALWAYS/NEVER 形式）。**Docker化やCIパイプラインが実際に要るときだけ**該当 SKILL を引く。Ansible/K8s/Helm/Jenkins まで含むが学生DS案件では過剰なので**丸ごと入れない**。既存CI（`.github/workflows/ai-verify.yml`）を直す時に dockerfile/github-actions 系だけ参照すると速い。導入前に中身をvet（[[safe-data-handling]]）。

## Workflow
1. 「誰がどこから触るか」「常時稼働か一時デモか」を確認。
2. 最小で足りるホスティングを選ぶ（迷ったら一時デモ前提で軽い方）。
3. 依存を固定し、秘密情報を env に逃がす。
4. 重い構成ファイルは委譲して書かせ、レビュー。
5. 公開前に [[ship-harden]]（秘密情報漏れ・想定外操作）を通す。

## Guardrails
- **公開＝外部送信**。クライアント情報・キーが乗らないか出す前に必ず確認。一度出たものはキャッシュ/インデックスされうる。
- 学生案件で過剰なインフラ（k8s等）を組まない。スコープを [[work-implementation]] で確認。
- 本番運用・監視が要るならそれは [[mlops]] / 別途設計の領域。
