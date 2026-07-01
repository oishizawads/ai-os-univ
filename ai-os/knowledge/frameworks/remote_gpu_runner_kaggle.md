---
title: "リモートGPUを実行環境にする（Colab/Kaggle/RunPod）"
type: playbook
domain: ml
tags: [kaggle, colab, kaggle-notebook, runpod, remote-ssh, gpu, reproducibility, experiment-management, hydra]
created: 2026-06-05
source:
  title: "HydraやPythonスクリプトで実験管理したいけどGPUがない人向け 無料GPUハック3選"
  author: "Kaggler community (Notion/Qiita 経由・出典記事)"
  isbn: ""
  chapter: ""
---

## Summary
ローカルGPUを持たない人が、Colab/Kaggle Notebook の無料GPUを「単なる実行環境」として使うための型。
中核は **「コード編集はローカル/Git で行い、クラウド側の Notebook は1セル目で `!python run.py` を叩くだけのスイッチにする」**。
これは [[notebook-workflow]]（クリーンカーネル・ロジックは src/ に抽出・papermill）のリモートGPU版であり、矛盾しない補完。
手段は実質「Drive同期」か「git clone」の2択。VSCode Colab拡張は単独では成立せずこの2択に collapse する。

## 運用パターン（2026-06 決定）
「ローカルのVSCode＋AI(Claude Code)で開発する流れを崩さない」ことを最優先に、**Colab往復モデル**を採用する。

| 優先度 | 構成 | 体験 | コスト |
|--------|------|------|--------|
| **本命** | **Colab Pro+ 往復モデル**：ローカルでAI開発→`git push`→Colabランチャーセルで実行→WandBで監視 | 開発はローカルのまま／**バックグラウンド実行**でタブを閉じて放置できる | compute units課金（止め忘れ注意） |
| 無料 | **git thin-switch**（Colab/Kaggle無料枠） | 往復＋揮発・切断あり | 無料 |

- **本命=往復モデルの肝は Colab Pro+ のバックグラウンド実行**。「pushしてセル叩いて、タブ閉じて放置→WandBで眺める」が成立する（無料枠の切断・時間制限が消える）。babysitでよければ Pro。
- **往復モデルの固定ルール**：永続化はDrive（データ・出力ckpt・重いwheelキャッシュ）、コードはgit、ランチャーは `mount→git pull→pip install→python run.py` の1〜2セルに固定して育てない。checkpointは optimizer/scheduler 込みで保存し再開に強くする。

## Core Principles
- **Notebook = thin switch**。学習ロジックを Notebook に直書きしない。`run.py` + 設定（Hydra等）を `src/` に置き、Notebook は呼び出すだけ。
- **再現性は手段に依存しない**。どの方式でも「コードの真実は Git/ローカル側」に一元化する。
- **秘密情報は出力にもコミットにも残さない**（[[safe-data-handling]]）。トークンを URL 直書きしない。

## Decision Rules
3手段の使い分け：

| 方式 | I/O速度 | 環境クリーンさ | 初期設定 | 画像大量コンペ適性 |
|------|---------|----------------|----------|--------------------|
| **1. Drive マウント**（Colab） | 遅い（Drive I/O） | △ 残留あり | 楽（git不要） | ✕ 学習が落ちる |
| **2. git clone**（Colab/Kaggle両対応） | 速い | ◎ 毎回クリーン | やや面倒（PAT管理） | ◎ |
| **3. VSCode Colab拡張** | — | — | 数クリック | 実質1か2に collapse |

- **画像大量コンペ / 速度重視** → **方式2（git clone）**。Drive I/O 遅延を回避。
- **手軽さ優先・git不慣れ・軽量データ** → **方式1（Drive）**。VSCodeで上書き保存→数秒でDrive反映。
- **ブラウザを開きたくないだけ** → 方式3を方式1/2の上に乗せる（後述の落とし穴に注意）。
- **トークンは必ず Kaggle Secrets / Colab Secrets 経由**。`!git clone https://{TOKEN}@...` を Notebook に直書きしない。

## Procedure
**方式1：Drive マウント（Colab）**
```python
from google.colab import drive
drive.mount('/content/drive')
%cd /content/drive/MyDrive/kaggle-project/experiments/exp001_resnet
!pip install -r ../../requirements.txt
!python run.py learning_rate=0.005
```

**方式2：git clone（Colab/Kaggle）**
```python
import os, subprocess, sys

token = os.environ["GITHUB_PAT"]  # ← Colab Secrets / Kaggle Secrets から注入（空でないこと）
REPO  = f"https://{token}@github.com/your-name/kaggle-project.git"
DST   = "/content/kaggle-project"

# clone は -b でブランチ指定（裸の位置引数は "Too many arguments" になる）。check=True で失敗時に止める
subprocess.run(["git", "clone", "-b", "main", REPO, DST], check=True)
os.chdir(f"{DST}/experiments/exp001_resnet")

# 実在する requirements を選び、失敗を握りつぶさない
req = next((f for f in ("../../requirements.txt", "requirements.txt") if os.path.exists(f)), None)
assert req, f"requirements が無い: {os.listdir('.')}"
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", req], check=True)

subprocess.run([sys.executable, "run.py"], check=True)
```
（コード修正のたびに `git push` が必要。実行環境は毎回クリーン。）
- **`!git clone` ではなく `subprocess.run(..., check=True)`** を使う。`!` セルは終了コードを無視するため、clone/pip が失敗しても `[ok] ...` を素通りで出して**空ディレクトリのまま学習を回す**事故が起きる。
- ブランチ指定は **`-b <branch>`**。`git clone <url> <branch> <dir>` のように裸で渡すと位置引数が多すぎて `Too many arguments` で落ちる。

**方式3：VSCode Google Colab拡張**
1. 拡張機能から「Google Colab」（必要なら Jupyter も）をインストール。
2. `.ipynb` を開き「カーネルの選択」→「Colab」→ ランタイム選択 → Googleサインイン。

## Anti-patterns
- **トークンを clone URL に直書き** → Notebook 出力・履歴・コミットにトークンが残り漏洩。必ず Secrets 経由。
- **VSCode拡張だけで `.py` を回せると思い込む** → 拡張は「ローカルのセルのコードをColabサーバーへ送って実行し結果を返す」仕組み。**サーバーはローカルディスクを見れない**ため、ローカルにある `run.py` を `!python run.py` しても「ファイルが無い」エラーになる。結局 Drive同期 or git clone が必要で、拡張は"ブラウザを開かずに済む"差にすぎない。
- **画像大量コンペで Drive マウント** → Drive I/O がボトルネックになり学習が遅くなる。git clone に切り替える。
- **Notebook にロジック直書き** → 再現性が壊れる。`src/` + `run.py` に寄せる（[[notebook-workflow]]）。
- **GPU 未接続のまま学習を回す** → ランタイムに GPU が付いていないと `torch ...+cpu` / `cuda available: False` のまま CPU 学習になり激遅。1セル目で `assert torch.cuda.is_available()` を入れて早期に落とす。Colab は ランタイム→ランタイムのタイプを変更→GPU で切替。

## Example
ローカルGPU無しで画像コンペを回す：
1. ロジックは `src/` に、エントリは `experiments/exp001/run.py`（Hydra設定）。
2. GitHub（private）にpush、PATは Colab Secrets に登録。
3. Colab Notebook 1セル目で Secrets からトークン取得 → `git clone` → `%cd` → `!python run.py`。
4. 学習ログ/成果物は Drive か Kaggle Dataset に書き出し、コミットには焼き込まない。

## GPU調達先の比較（ローカルGPU無しの場合）
| 調達先 | 立ち位置 |
|--------|----------|
| Colab | コスパ良。手軽。まずはここ |
| Kaggle Notebook | 無料GPU＋データ直結。週時間制限あり |
| Vast AI | 最安・自由度高（玄人向け） |
| RunPod | 使いやすさのバランス良 |
| Google Cloud | 割高 |
| 大学サーバ / tsubame(H100) | 所属で使えるなら最強（東工大はtsubameでH100可） |

- **Kaggle MCP**：Kaggle datasets を自然言語で操作できる。データ取り込みの省力化に。
- **落とし穴 — Notebook Timeout**：高評価の公開コードでも、実行環境やCPU中心の重い処理だと制限時間内に終わらないことがある。そのまま実行＝完走ではない。

## Eval
- Notebook 本体に学習ロジックが直書きされていない（1セルのランチャーになっている）。
- トークンが Notebook 出力・コミットに残っていない（Secrets 経由）。
- 「コードの真実」が Git/ローカル側に一元化され、クラウドは使い捨て。
- 画像大量コンペで Drive I/O をボトルネックにしていない。

## 参考
- https://developers.googleblog.com/en/google-colab-is-coming-to-vs-code/
- Kaggle Dataset は Colab から直接利用可能（運用時はこれも併用）。
