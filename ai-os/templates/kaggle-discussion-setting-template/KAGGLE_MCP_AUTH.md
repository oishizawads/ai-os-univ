# Kaggle MCP 認証セットアップ

`https://www.kaggle.com/mcp` は OAuth2 の `client_secret_basic` フローを要求するが、
Claude Code 側に Kaggle 専用の OAuth アプリ資格情報（clientId/clientSecret）が無く、
通常の `/mcp auth` や `mcp__kaggle__authenticate` フローは失敗する。

代わりに `~/.claude.json` の MCP 設定に **Basic 認証ヘッダーを直接付与**する方式で接続できる。
Kaggle の MCP HTTP エンドポイントは Basic 認証も受け付けるため、これで動作する。

## 手順

1. Kaggle API トークン (`~/.kaggle/kaggle.json`) を用意する
   - 無ければ Kaggle Account ページ → "Create New Token" でダウンロード
   - 配置: `~/.kaggle/kaggle.json`（パーミッション 600 推奨）

2. Basic 認証文字列を生成

   ```bash
   python3 -c "
   import json, base64
   with open('/home/$USER/.kaggle/kaggle.json') as f:
       k = json.load(f)
   cred = base64.b64encode(f\"{k['username']}:{k['key']}\".encode()).decode()
   print(f'Basic {cred}')
   "
   ```

3. `~/.claude.json` の `mcpServers` に以下を追加（または既存 `kaggle` エントリを置換）

   ```json
   "kaggle": {
     "type": "http",
     "url": "https://www.kaggle.com/mcp",
     "headers": {
       "Authorization": "Basic <手順2の出力>"
     }
   }
   ```

4. Claude Code を再起動して MCP ツール一覧に `mcp__kaggle__*` が現れることを確認

## 注意

- API キーを再発行したら `kaggle.json` と `~/.claude.json` の両方を更新すること
- `~/.claude.json` は機微情報を含むので共有・公開しない
