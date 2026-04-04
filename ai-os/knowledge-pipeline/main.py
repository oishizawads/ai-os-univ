"""knowledge-pipeline エントリポイント

通常フロー:
  Web Clipper で記事をクリップ → raw/ に保存
  python main.py --ingest        # 要約生成 + _INDEX.md 更新 + ChromaDB 登録（1コマンドで完結）
  python main.py --query "..."   # RAG検索 → Claude回答 → reports/ に保存 → ChromaDB に自動登録
  python main.py --search "..."  # キーワード検索

状態確認:
  python main.py --status        # ChromaDB とvaultの同期状態を確認

定期メンテナンス（週1程度）:
  python main.py --compile       # _INDEX.md からコンセプトwikiページを生成
  python main.py --lint          # wiki健全性チェック
  python main.py --reindex       # ChromaDB を vault 全体から再構築（破損・初回セットアップ時）

その他:
  python main.py --search-ui     # 検索Web UIを起動（port 8766）
  python main.py --idea "..."    # アイデアを整形して vault に保存
  python main.py --report "..."  # 指定トピックの包括レポートを生成
  python main.py --context "..."  # CONTEXT.md生成
  python main.py --analyze       # 知識グラフ定量分析
"""
import argparse
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()


def _setup_logging(cfg: dict):
    log_dir = Path(cfg["logging"]["dir"])
    log_dir.mkdir(exist_ok=True)
    level = getattr(logging, cfg["logging"].get("level", "INFO").upper(), logging.INFO)
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / "pipeline.log", encoding="utf-8"),
    ]
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )


def load_config(path: str = "config.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# --- ingest ---

def phase_ingest(cfg: dict):
    from src.ingest.processor import process_new_files
    count = process_new_files(cfg)
    print(f"\n処理完了: {count} 件")


# --- embed ---

def phase_reindex(cfg: dict):
    """vault 全体を ChromaDB に再登録（メンテナンス用）"""
    from src.rag.embedder import Embedder
    logger = logging.getLogger("reindex")
    embedder = Embedder(cfg)
    total = embedder.embed_vault(cfg["vault"])
    logger.info("Reindex complete. Total new entries: %d", total)


def phase_status(cfg: dict):
    """ChromaDB とvaultの同期状態を表示"""
    import chromadb
    from chromadb.config import Settings
    from src.ingest.index import get_indexed_files
    from pathlib import Path

    vault_root = Path(cfg["vault"]["path"])
    vault_cfg = cfg["vault"]

    # vault のmd数
    vault_md_count = len([p for p in vault_root.rglob("*.md") if not p.name.startswith("_") and "_templates" not in str(p)])

    # raw/ のmd数
    raw_dir = vault_root / vault_cfg.get("raw_dir", "raw")
    raw_count = len([p for p in raw_dir.glob("*.md") if p.name != "_INDEX.md"]) if raw_dir.exists() else 0

    # _INDEX.md の登録数
    indexed_count = len(get_indexed_files(vault_cfg))

    # ChromaDB のエントリ数（ユニークdoc数）— モデルロードなしで直接アクセス
    try:
        db_cfg = cfg["database"]
        chroma_path = Path(db_cfg["chroma_dir"])
        chroma_client = chromadb.PersistentClient(
            path=str(chroma_path),
            settings=Settings(anonymized_telemetry=False),
        )
        collection = chroma_client.get_or_create_collection(
            name=db_cfg.get("collection_name", "knowledge_base"),
        )
        all_entries = collection.get(include=["metadatas"])
        chroma_docs = len({m.get("source_file", "") for m in all_entries["metadatas"]})
        chroma_entries = len(all_entries["ids"])
    except Exception as e:
        chroma_docs = -1
        chroma_entries = -1

    print("\n=== Knowledge Base Status ===")
    print(f"  vault/raw/ ファイル数:      {raw_count}")
    print(f"  _INDEX.md 登録数:           {indexed_count}")
    print(f"  vault 全体 .md 数:          {vault_md_count}")
    print(f"  ChromaDB 登録doc数:         {chroma_docs}")
    print(f"  ChromaDB エントリ数(chunk): {chroma_entries}")
    if raw_count > indexed_count:
        print(f"\n  ⚠ 未処理ファイルあり: {raw_count - indexed_count} 件 → --ingest を実行してください")


# --- query (RAG → Claude → save) ---

def phase_query(query: str, top_k: int, cfg: dict):
    import anthropic
    from src.rag.retriever import Retriever

    logger = logging.getLogger("query")
    retriever = Retriever(cfg)
    docs = retriever.query(query, top_k=top_k)

    if not docs:
        print("関連ドキュメントが見つかりませんでした。--ingest または --reindex を実行してください。")
        return

    logger.info("%d 件のdocを取得", len(docs))

    # ドキュメント全文をコンテキストとして組み立て
    context_parts = []
    for d in docs:
        context_parts.append(
            f"## {d['title']}\nファイル: {d['filename']}  URL: {d['url']}\n\n{d['content']}"
        )
    context = "\n\n---\n\n".join(context_parts)

    system_prompt = """あなたは知識ベースの情報をもとに質問に回答するアシスタントです。
提供されたドキュメントを参照して、正確で詳細な回答をMarkdown形式で作成してください。
回答の末尾には「## 参照ドキュメント」セクションを設け、使用したドキュメントを列挙してください。"""

    user_prompt = f"""以下のドキュメントを参照して質問に回答してください。

# 質問
{query}

# 参照ドキュメント
{context}
"""

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    claude_cfg = cfg["claude"]

    logger.info("Claude APIで回答生成中...")
    try:
        resp = client.messages.create(
            model=claude_cfg["model"],
            max_tokens=4000,
            temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        answer = resp.content[0].text
        usage = resp.usage
        logger.info("Claude API: input=%d output=%d tokens", usage.input_tokens, usage.output_tokens)
    except Exception as e:
        logger.error("Claude API error: %s", e)
        return

    # reports/ に保存
    vault_root = Path(cfg["vault"]["path"])
    reports_dir = vault_root / cfg["vault"].get("reports_dir", "reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = re.sub(r"[^\w\u3040-\u30ff\u4e00-\u9fff]", "_", query)[:40].strip("_")
    out_path = reports_dir / f"qa_{date_str}_{slug}.md"

    frontmatter = f"---\ntitle: \"{query}\"\ntype: qa\ndate: {datetime.now().strftime('%Y-%m-%d')}\nsources: {[d['filename'] for d in docs]}\n---\n\n"
    out_path.write_text(frontmatter + answer, encoding="utf-8")

    # reports/ に保存した回答を ChromaDB に登録（filing back）
    try:
        from src.rag.embedder import Embedder
        embedder = Embedder(cfg)
        embedder.embed_file(out_path, {"title": query, "type": "qa", "published": datetime.now().strftime("%Y-%m-%d"), "url": ""})
        logger.info("回答を ChromaDB に登録しました")
    except Exception as e:
        logger.warning("回答の embedding 失敗（非致命的）: %s", e)

    print(f"\n回答を保存しました: {out_path}")
    print(f"参照doc数: {len(docs)}")
    print("\n--- 回答プレビュー（先頭500文字）---")
    print(answer[:500])


# --- search ---

def phase_search(query: str, cfg: dict, top_k: int = 10):
    from src.search.engine import search
    vault_root = Path(cfg["vault"]["path"])
    results = search(query, vault_root, top_k=top_k)

    if not results:
        print("該当なし")
        return

    print(f"\n=== 検索結果: {len(results)} 件 ===\n")
    for r in results:
        print(f"[{r['score']:.2f}] {r['title']}")
        print(f"       {r['relative']}")
        print(f"       {r['snippet']}\n")


# --- idea ---

def phase_idea(text: str, cfg: dict):
    import anthropic
    from src.formatter.idea_template import IDEA_SYSTEM_PROMPT, build_idea_prompt
    from src.writer.obsidian import write
    from src.rag.embedder import Embedder

    logger = logging.getLogger("idea")
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    claude_cfg = cfg["claude"]

    try:
        response = client.messages.create(
            model=claude_cfg["model"],
            max_tokens=claude_cfg["max_tokens"],
            temperature=claude_cfg["temperature"],
            system=IDEA_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_idea_prompt(text)}],
        )
        md = response.content[0].text
    except Exception as e:
        logging.getLogger("idea").error("Claude API error: %s", e)
        return

    title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', md, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else text[:50]

    article = {
        "url": "",
        "title": title,
        "published": datetime.now().strftime("%Y-%m-%d"),
        "type": "idea",
        "tags": ["idea"],
        "source_name": "manual",
    }

    path = write(article, md, cfg)
    if not path:
        logger.error("Vault保存失敗")
        return

    logger.info("Saved: %s", path)
    try:
        embedder = Embedder(cfg)
        n = embedder.embed_file(path, article)
        logger.info("Embedded %d entries", n)
    except Exception as e:
        logger.warning("Embedding失敗（非致命的）: %s", e)

    print(f"\n保存先: {path}")


# --- context ---

def phase_context(query: str, mode: str, top_k: int, cfg: dict):
    import anthropic
    from src.rag.retriever import Retriever
    from src.formatter.context_template import PROMPTS

    logger = logging.getLogger("context")
    if mode not in PROMPTS:
        logger.error("未対応のmode: %s (work / comp)", mode)
        return

    retriever = Retriever(cfg)
    docs = retriever.query(query, top_k=top_k)
    if not docs:
        logger.warning("関連ドキュメントが見つかりませんでした。")
        return

    system_prompt, build_prompt = PROMPTS[mode]
    user_prompt = build_prompt(query, docs)

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    claude_cfg = cfg["claude"]
    try:
        response = client.messages.create(
            model=claude_cfg["model"],
            max_tokens=claude_cfg["max_tokens"],
            temperature=claude_cfg["temperature"],
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        content = response.content[0].text
    except Exception as e:
        logger.error("Claude API error: %s", e)
        return

    output_path = _resolve_context_output(query, mode, cfg)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    print(f"\n保存先: {output_path}")


def _resolve_context_output(query: str, mode: str, cfg: dict) -> Path:
    contexts_cfg = cfg.get("contexts", {}).get(mode, []) or []
    for entry in contexts_cfg:
        if not isinstance(entry, dict):
            continue
        if entry.get("name", "") and entry["name"] in query or query in entry.get("name", ""):
            return Path(entry["output"])
    vault_root = Path(cfg["vault"]["path"])
    reports_dir = vault_root / cfg["vault"].get("reports_dir", "reports")
    date_str = datetime.now().strftime("%Y%m%d")
    slug = re.sub(r"[^\w\u3040-\u30ff\u4e00-\u9fff]", "_", query)[:40].strip("_")
    return reports_dir / f"context_{mode}_{date_str}_{slug}.md"


# --- compile ---

def phase_compile(cfg: dict, force: bool = False, batch_size: int = 10):
    from src.compiler.wiki import compile_wiki
    compile_wiki(cfg, force=force, batch_size=batch_size)


# --- lint ---

def phase_lint(cfg: dict):
    from src.analysis.lint import run_lint
    out_path = run_lint(cfg)
    print(f"\nLintレポート保存先: {out_path}")


# --- report ---

def phase_report(query: str, top_k: int, fmt: str, cfg: dict):
    import anthropic
    from src.rag.retriever import Retriever
    from src.formatter.report_template import (
        REPORT_SYSTEM_PROMPT, build_report_prompt,
        MARP_SYSTEM_PROMPT, build_marp_prompt,
    )

    logger = logging.getLogger("report")
    vault_root = Path(cfg["vault"]["path"])
    reports_dir = vault_root / cfg["vault"].get("reports_dir", "reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    retriever = Retriever(cfg)
    docs = retriever.query(query, top_k=top_k)
    if not docs:
        logger.warning("関連ドキュメントが見つかりませんでした。")
        return

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    claude_cfg = cfg["claude"]

    if fmt == "marp":
        system_prompt = MARP_SYSTEM_PROMPT
        user_prompt = build_marp_prompt(query, docs)
        prefix = "slides"
    else:
        system_prompt = REPORT_SYSTEM_PROMPT
        user_prompt = build_report_prompt(query, docs)
        prefix = "report"

    try:
        resp = client.messages.create(
            model=claude_cfg["model"],
            max_tokens=4000,
            temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        content = resp.content[0].text
    except Exception as e:
        logger.error("Claude API error: %s", e)
        return

    date_str = datetime.now().strftime("%Y%m%d")
    slug = re.sub(r"[^\w\u3040-\u30ff\u4e00-\u9fff]", "_", query)[:40].strip("_")
    out_path = reports_dir / f"{prefix}_{date_str}_{slug}.md"
    out_path.write_text(content, encoding="utf-8")

    # 生成レポートを ChromaDB に登録（filing back）
    try:
        from src.rag.embedder import Embedder
        embedder = Embedder(cfg)
        embedder.embed_file(out_path, {"title": query, "type": "report", "published": datetime.now().strftime("%Y-%m-%d"), "url": ""})
        logger.info("レポートを ChromaDB に登録しました")
    except Exception as e:
        logger.warning("レポートの embedding 失敗（非致命的）: %s", e)

    print(f"\n保存先: {out_path}")
    print(f"使用doc数: {len(docs)}")


# --- main ---

def main():
    parser = argparse.ArgumentParser(description="knowledge-pipeline")
    parser.add_argument("--ingest", action="store_true", help="raw/新規ファイルを処理（要約+_INDEX.md+ChromaDB）")
    parser.add_argument("--status", action="store_true", help="ChromaDBとvaultの同期状態を表示")
    parser.add_argument("--reindex", action="store_true", help="ChromaDBをvault全体から再構築（メンテナンス用）")
    parser.add_argument("--query", type=str, default=None, help="RAG検索→Claude回答→reports/に保存")
    parser.add_argument("--top-k", type=int, default=5, help="検索件数（デフォルト: 5）")
    parser.add_argument("--search", type=str, default=None, help="naiveテキスト検索")
    parser.add_argument("--search-ui", action="store_true", help="検索Web UIを起動（port 8766）")
    parser.add_argument("--port", type=int, default=8766, help="--search-ui のポート番号")
    parser.add_argument("--idea", type=str, default=None, help="アイデアを整形してVaultに保存")
    parser.add_argument("--context", type=str, default=None, help="CONTEXT.md生成クエリ")
    parser.add_argument("--mode", type=str, default="work", choices=["work", "comp"])
    parser.add_argument("--compile", action="store_true", help="Wikiコンセプトページを自動生成")
    parser.add_argument("--compile-force", action="store_true", help="既存ページも強制再生成")
    parser.add_argument("--compile-batch", type=int, default=10)
    parser.add_argument("--lint", action="store_true", help="Wiki健全性チェックレポート")
    parser.add_argument("--report", type=str, default=None, help="指定トピックの包括レポートを生成")
    parser.add_argument("--format", type=str, default="markdown", choices=["markdown", "marp"])
    parser.add_argument("--analyze", action="store_true", help="知識グラフ定量分析")
    parser.add_argument("--watch", action="store_true", help="raw/ を監視して自動 ingest（常駐プロセス）")
    parser.add_argument("--auto-compile", action="store_true", help="--watch 時に vault 変更でも auto compile")
    parser.add_argument("--config", type=str, default="config.yaml")
    args = parser.parse_args()

    cfg = load_config(args.config)
    _setup_logging(cfg)

    if args.ingest:
        phase_ingest(cfg)
    elif args.status:
        phase_status(cfg)
    elif args.reindex:
        phase_reindex(cfg)
    elif args.query:
        phase_query(args.query, args.top_k, cfg)
    elif args.search:
        phase_search(args.search, cfg, top_k=args.top_k)
    elif args.search_ui:
        from src.search.web_ui import start_search_ui
        start_search_ui(cfg, port=args.port)
    elif args.idea:
        phase_idea(args.idea, cfg)
    elif args.context:
        phase_context(args.context, args.mode, args.top_k, cfg)
    elif args.compile or args.compile_force:
        phase_compile(cfg, force=args.compile_force, batch_size=args.compile_batch)
    elif args.lint:
        phase_lint(cfg)
    elif args.report:
        phase_report(args.report, args.top_k, args.format, cfg)
    elif args.analyze:
        from src.analysis.graph import run_analysis
        run_analysis(cfg)
    elif args.watch:
        from src.watcher.watcher import start_watcher
        start_watcher(cfg, auto_compile=args.auto_compile)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
