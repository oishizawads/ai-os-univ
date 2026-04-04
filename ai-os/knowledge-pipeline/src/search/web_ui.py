"""シンプルな検索Web UI"""
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .engine import search as run_search

logger = logging.getLogger(__name__)

_HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Knowledge Search</title>
<style>
  body { font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; }
  h1 { font-size: 1.4rem; margin-bottom: 20px; }
  input[type=text] { width: calc(100% - 90px); padding: 8px 12px; font-size: 1rem; border: 1px solid #ccc; border-radius: 4px; }
  button { padding: 8px 16px; font-size: 1rem; background: #444; color: #fff; border: none; border-radius: 4px; cursor: pointer; margin-left: 8px; }
  #results { margin-top: 24px; }
  .result { border-bottom: 1px solid #eee; padding: 12px 0; }
  .result-title { font-size: 1rem; font-weight: bold; color: #1a0dab; }
  .result-path { font-size: 0.75rem; color: #888; margin: 2px 0; }
  .result-snippet { font-size: 0.85rem; color: #555; }
  .score { font-size: 0.75rem; color: #aaa; }
  #status { color: #888; font-size: 0.85rem; margin-top: 8px; }
</style>
</head>
<body>
<h1>Knowledge Search</h1>
<div>
  <input type="text" id="q" placeholder="検索キーワード（スペース区切りでAND）" autofocus>
  <button onclick="doSearch()">検索</button>
</div>
<div id="status"></div>
<div id="results"></div>
<script>
async function doSearch() {
  const q = document.getElementById('q').value.trim();
  if (!q) return;
  document.getElementById('status').textContent = '検索中...';
  document.getElementById('results').innerHTML = '';
  const res = await fetch('/search?q=' + encodeURIComponent(q));
  const data = await res.json();
  document.getElementById('status').textContent = data.total + ' 件ヒット';
  const container = document.getElementById('results');
  data.results.forEach(r => {
    const div = document.createElement('div');
    div.className = 'result';
    div.innerHTML = `
      <div class="result-title">${r.title}</div>
      <div class="result-path">${r.relative} <span class="score">score: ${r.score.toFixed(2)}</span></div>
      <div class="result-snippet">${r.snippet}</div>
    `;
    container.appendChild(div);
  });
}
document.getElementById('q').addEventListener('keydown', e => { if (e.key === 'Enter') doSearch(); });
</script>
</body>
</html>"""


def start_search_ui(cfg: dict, port: int = 8766):
    import uvicorn

    vault_root = Path(cfg["vault"]["path"])
    app = FastAPI(title="Knowledge Search")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    @app.get("/", response_class=HTMLResponse)
    async def index():
        return _HTML

    @app.get("/search")
    async def search_api(q: str = "", top_k: int = 10):
        if not q:
            return {"results": [], "total": 0}
        results = run_search(q, vault_root, top_k=top_k)
        return {
            "results": [
                {
                    "title": r["title"],
                    "relative": r["relative"],
                    "score": r["score"],
                    "snippet": r["snippet"],
                }
                for r in results
            ],
            "total": len(results),
        }

    logger.info("Search UI起動: http://127.0.0.1:%d", port)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
