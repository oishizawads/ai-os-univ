# Capability Map — 領域カバレッジと正典

> 設計思想: **DS/MLE の背骨は深く確実に。周辺領域は「1領域1正典 ＋ 品質層常駐 ＋ 重実装は委譲」で、背骨を圧迫せず一気通貫（FDE）で回せるようにする。**
>
> 対になる **[[META_MAP]]**（`.claude/META_MAP.md`）＝「どう回すか」の運用OS（集める・考える・決める・動かす・検証・伝える・残す・改善の8観点）。このマップが"何をやるか"、META_MAPが"どう回すか"。

## 3つの規律
1. **1領域1正典** — 各領域で従うスキルは1本だけ。役割を被らせない／メガコレクションを入れない。迷いと衝突とコンテキスト肥大を防ぐ。
2. **品質層は常駐** — 領域横断の仕上げ（[[stop-slop]] / [[ui-polish]] / [[ship-harden]]）は全成果物に通す標準ゲート。専門外ほど出る"素人っぽい粗"を全領域で拾う。
3. **重実装も Claude 直接が既定** — フロント・バックエンド・インフラも Claude が実装まで担う（必要時に領域正典を引く）。委譲は任意（ユーザーが振った時 or トークン/スループットに実利がある時）。

## ロード方針
| 層 | ロード | 厚み |
|---|---|---|
| 背骨（DS/MLE） | 常駐 | 深く |
| 領域正典（UI/フロント/インフラ…） | **オンデマンド**（その文脈でだけ） | 1領域1本 |
| 品質層 | 常駐 | 少数 |

→ 22領域ぶんの知識をディスクに置いても、常時コンテキストに乗るのは品質層だけ。これで「全領域カバー」と「背骨を圧迫しない」を両立する。

## 領域 → 正典 対応表
狙うレベル: **深**=判断される/内製必須 ／ **適**=恥ずかしくない程度 ／ **委**=委譲前提（仕様＋判断だけ）

### 背骨（専門・既存）
| 領域 | 狙う | 正典（現状） |
|---|---|---|
| 1. データサイエンス | 深 | [[experiment-workflow]] / eda / [[viz-style]] / [[sql-analysis]] / decision-lab |
| 2. 機械学習エンジニアリング | 深 | [[experiment-workflow]] / [[python-ops]] / [[review-exp]] |

### 作る（実装）
| 領域 | 狙う | 正典 |
|---|---|---|
| 3. データエンジニアリング | 適〜深 | [[sql-analysis]] / [[path-io]] / [[safe-data-handling]] / [[dataframe-polars]] |
| 4. バックエンド開発 | 委 | 委譲(Codex/OpenCode) ＋ [[python-style]] |
| 5. フロントエンド実装 | 委 | **[[frontend-build]]**（spec＋委譲） |
| 6. UI/UXデザイン | 適 | **[[ui-ux-design]]**（任意DB: ui-ux-pro-max） |
| 7. インフラ/DevOps/デプロイ | 適〜委 | **[[infra-deploy]]** |
| 8. MLOps | 適〜深 | **[[mlops]]**（WandB） |
| 9. ソフトウェア品質 | 深 | [[review-exp]] / work-review / security-review ＋ [[ship-harden]] |

### 伝える・売る（ビジネス／対人）
| 領域 | 狙う | 正典 |
|---|---|---|
| 10. PM／要件定義 | 深 | [[work-implementation]] / .steering / plan |
| 11. ビジネス戦略／コンサル | 深 | knowledge/frameworks / decision-lab |
| 12. ライティング／コピー | 深 | **[[stop-slop]]** |
| 13. プレゼン／スライド | 適〜深 | [[slides-maker]] / pptx / slidekit |
| 14. 事業開発／ピッチ／営業 | 適 | frameworks（要時にコピー正典を1本） |
| 15. 交渉／クライアント折衝 | 適 | 都度（軽め） |
| 16. マーケ／グロース／SEO | 適（低優先） | 未（需要が出たら1本） |
| 17. 効果測定／アナリティクス | 深 | [[experiment-workflow]] / decision-lab（DS隣接） |

### 支える（横断・運用）
| 領域 | 狙う | 正典 |
|---|---|---|
| 18. ドメイン知識（案件業界） | 案件次第 | [[survey-papers]] ＋ 都度リサーチ |
| 19. リサーチ／論文調査 | 適 | [[survey-papers]] / research |
| 20. プロジェクト運営／ナレッジ | 適 | ai-os 本体 / [[meeting-log]] |
| 21. AIオーケストレーション | 適 | 直接委譲: /codex-coder / /opencode-coder / /gemini-coder |

### 高度・専門（分析）
| 領域 | 狙う | 正典 |
|---|---|---|
| 22. 因果推論 | 深 | [[causal-inference]] / decision-lab |

## 新規追加（このマップで作ったもの）
- 領域正典（オンデマンド）: `ui-ux-design` / `frontend-build` / `infra-deploy` / `mlops` / `causal-inference`
- 品質層（常駐）: `stop-slop` / `ui-polish` / `ship-harden`

## 外部スキル精査結果（2026-06-18・「人気でなく中身で選ぶ」）
コミュニティ良品を実体確認し、自前と突き合わせた結果:
- **stop-slop**: wpgaurav/claude-code-skills(MIT)の構造アンチパターン/スコアリングを採用し格上げ済み。
- **ui-ux-design**: nextlevelbuilder/ui-ux-pro-max(MIT)のチャート選択DBを `references/chart-selection.csv` にvendor（25種・選択判断が viz-style より深い）。
- **ui-polish / ship-harden**: wpgaurav harden/polishから具体だけ吸収、純Web項目はfrontend-buildへ切り分け。
- **infra-deploy**: akin-ozer/cc-devops-skills(Apache-2.0)を Docker/CI 時のオンデマンド参照に。丸入れせず（K8s/Helm等は過剰）。
- **mlops / frontend-build**: コミュニティ候補はLLM研究/汎用Web向けで非適合。自前維持（各SKILLの精査メモ参照）。
- **却下**: メガコレクション（alirezarezvani 337 / LibreUIUX 152 等）は偽の広さ＝背骨を圧迫するため発見用途のみ。

## 拡張ルール（今後領域を足すとき）
1. **既存正典のある領域は触らない**（表を見て重複を避ける）。
2. 新領域は**正典1本**だけ。外部リポジトリは丸コピせず、正典から「任意で引く参照」にする（`SKILL.md`とスクリプトを入れる前に必ず読む）。
3. 追加後は **context-budget スキルで増分を測る**。背骨を圧迫したら戻す。
