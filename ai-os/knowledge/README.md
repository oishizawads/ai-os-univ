# ai-os/knowledge/ 構成ガイド

技術書・ビジネス本・フレームワーク本を「使える知見」に圧縮して保存する場所。

## 基本方針

- **raw 全文は保存しない**。章立てではなく「課題・判断・手順」単位で分解する
- **1冊から複数の知見ファイルを作る**
- **自分の言葉で再構成**し、`TEMPLATE.md` のフォーマットに厳密に従う
- **ファイル命名は `{概念名}_{元本略称}.md`**（検索しやすさ優先）

## ディレクトリ構成

```
ai-os/knowledge/
├── TEMPLATE.md              # 知見ファイルの作成テンプレート
├── README.md                # このファイル
├── frameworks/              # 技術・エンジニアリング系フレームワーク
│   ├── clean_code.md
│   ├── feature_engineering.md
│   └── model_selection.md
├── business_frameworks/     # ビジネス・PM・自己啓発系フレームワーク
│   ├── product_discovery_inspired.md
│   └── identity_habits_atomic.md
├── principles/              # 判断基準・コーディング規約・設計原則
├── playbooks/               # 手順・ステップ・実践ワークフロー
├── failure_patterns/        # アンチパターン・失敗事例・落とし穴
├── evals/                   # 評価ルール・チェックリスト
├── glossaries/              # 用語定義
└── books/                   # パブリックドメイン・OCW本の原本（限定）
```

## 使い分け

| ディレクトリ | 入れるもの | 入れないもの |
|---|---|---|
| `frameworks/` | 技術設計、データサイエンス手法、エンジニアリングパターン | ビジネス戦略、マネジメント論、自己啓発 |
| `business_frameworks/` | プロダクトマネジメント、組織設計、戦略、生産性、自己啓発 | 技術的なアルゴリズムや設計パターン |
| `principles/` | 「こう判断する」基準、規約、哲学 | 手順書やフレームワーク全体 |
| `playbooks/` | 再現可能な手順、ワークフロー | 抽象的な原則だけ |
| `failure_patterns/` | やりがちな失敗とその原因 | 成功事例やベストプラクティス |

## 新規知見ファイル作成フロー

1. 本を読み、「この章で何が解決されるか」を特定
2. `TEMPLATE.md` に従って書き起こす
3. 適切な `domain` と `type` を選び、対応するディレクトリに保存
4. ファイル名は `{概念名}_{元本略称}.md`
5. `source` frontmatter に元本情報を明記

## 既存ファイルの移行指針

`frameworks/` 内に混在しているビジネス・自己啓発本（例：`atomic_habits.md`, `lean_startup.md` など）は、改修時に `business_frameworks/` へ移行する。
移行の際は、内容を `TEMPLATE.md` フォーマットに合わせて再構成すること。

## Kaggle 運用ナレッジ体系（LAIME Kaggle Dojo 由来 / 2026-06）

戦略 → 設定管理 → 実行 → 学習 → 追跡 → 記録 の縦串で相互リンク済み。Kaggle/コンペ作業時はまずここを参照。

**戦略・実務知（playbooks/）**
- `kaggle_medal_strategy.md` — 銅銀金の取り方、時間/チーム戦略、序盤参加の注意点
- `kaggle_experiment_strategy.md` — CV>LB、実験粒度、仮説駆動、誤り分析、aug実像、後処理、CV設計、LB probing
- `ssl_pseudo_label_kaggle.md` — SSL/擬似ラベルとリーク境界（Gen2リーク）
- `ai_agents_in_kaggle.md` — どこまでAIに任せるか（理解=人間 / 量産=AI）
- `kaggle_learning_resources.md` — 書籍・スライド・記事・リポジトリ・ツール索引

**実装・ツール（frameworks/）**
- `hydra_experiment_management.md` — .py+Hydra、メジャー/マイナー版フォルダ構成
- `remote_gpu_runner_kaggle.md` — Colab/Kaggleを実行環境化、GPU調達比較、コードコンペ
- `experiment_tracking_wandb.md` — WandB一本化（CSV台帳は廃止）
- `image_baseline_tuning_kaggle.md` — 画像ベースライン、I/O高速化、charm実践レシピ、EMA、aux loss
- `timm_usage.md` — モデルを1行で、特徴量抽出、pretrainedルール確認

メンター合意の核：**CV>LB（CV設計が差を生む）／ 仮説駆動＋1変更1実験 ／ 公開Notebookは理解してから ／ AIは量産・理解は人間 ／ リーク境界に敏感**。
