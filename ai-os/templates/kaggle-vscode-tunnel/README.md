# Kaggle × Colab × VSCode Tunnel

Colab のランタイム（GPU/Drive/データ）をローカル VSCode から直接触る運用テンプレ。
`vscode-colab` ライブラリで VSCode 公式の Remote Tunnels を立てる。

## ファイル

- `colab_tunnel.ipynb` — Colab にアップロードして使うスターターノート
- `kaggle_tunnel.ipynb` — Kaggle Notebook 用（必要なら）

## 一回だけの準備

1. **ローカル VSCode**: 拡張 `Remote - Tunnels`（発行元: Microsoft）をインストール
2. **GitHub アカウント**: Colab/Kaggle のサインインアカウントと同じ GitHub アカウントで VSCode にもサインインしておく
3. **Kaggle API token**: `~/.kaggle/kaggle.json` を用意（Kaggle Account ページ → "Create New Token"）

## 接続手順（毎回）

### Colab 側

1. <https://colab.research.google.com/> を開く
2. `colab_tunnel.ipynb` をアップロード
3. ランタイム → ランタイムのタイプを変更 → GPU を選択（必要なら）
4. セルを上から実行:
   - `pip install vscode-colab`
   - `vscode_colab.login()` → 表示された device code で GitHub 認証
   - `vscode_colab.connect(name="colab-kaggle", ...)` → tunnel URL が出る
5. （データ使う場合）Kaggle API セルで `kaggle.json` をアップロードしてコンペデータを取得

### ローカル VSCode 側

1. `Ctrl+Shift+P` → `Remote Tunnels: Connect to Tunnel...`
2. GitHub サインインを促されたら同じアカウントでサインイン
3. tunnel 名（既定 `colab-kaggle`）を選択
4. 接続完了。`/content/` が Colab ランタイムのファイルシステム

## 切れたら

- Colab タブを閉じる/ランタイムが切れる → tunnel も切れる
- 再開: Colab ノートを再実行（`login()` はキャッシュされていることが多い、`connect()` だけで足りるケース有り）

## トラブル

| 症状 | 対処 |
|------|------|
| `Remote Tunnels: Connect to Tunnel` が出ない | 拡張 `Remote - Tunnels` が未インストール。インストール後 VSCode 再起動 |
| GitHub 認証ループ | Colab とローカル VSCode のサインイン GitHub アカウントを揃える |
| Kaggle で `Copy Failed` 赤表示 | サンドボックス制限。device code は手入力すれば良い |
| `connect()` が `~5 分`止まる | `setup_python_version` 指定時は pyenv インストールで時間かかる仕様。指定しなければ即起動 |
| ランタイム切れで作業ロスト | コードは `git push` でGitHubに、データは `/content/drive/MyDrive/` 等の永続層に置く |

## Kaggle Notebook 直接接続版

GPU が Kaggle 側 (T4×2/週30h) で十分なら、`kaggle_tunnel.ipynb` を Kaggle Notebook にアップロードしても同じことができる。

ただし Kaggle Notebook は **GPU セッション制限と保存タイミング** がColabと違うので、
長時間学習なら Colab、軽量実験なら Kaggle、と使い分けるのが楽。

## 参考

- [vscode-colab — PyPI](https://pypi.org/project/vscode-colab/)
- [vscode-colab — GitHub](https://github.com/EssenceSentry/vscode-colab)
- [kaggle-vscode-remote-tunnel — Kaggle example notebook](https://www.kaggle.com/code/omidostovari/kaggle-vscode-remote-tunnel)
