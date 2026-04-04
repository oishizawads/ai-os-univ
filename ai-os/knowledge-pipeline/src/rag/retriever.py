"""ChromaDB RAG検索モジュール

ベクトル検索でdocを特定 → source_fileで重複排除 → ディスクから全文読み込み
"""
import logging
from pathlib import Path

from .embedder import Embedder

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self, cfg: dict):
        self.embedder = Embedder(cfg)
        self.model = self.embedder.model
        self.collection = self.embedder.collection

    def query(self, query_text: str, top_k: int = 5) -> list[dict]:
        """ベクトル検索 → doc単位に重複排除 → 全文返却"""
        candidate_k = min(top_k * 6, 60)

        query_emb = self.model.encode(query_text, normalize_embeddings=True).tolist()
        results = self.collection.query(
            query_embeddings=[query_emb],
            n_results=candidate_k,
            include=["metadatas", "distances"],
        )

        if not results["ids"] or not results["ids"][0]:
            return []

        # source_fileで重複排除（同じdocの複数チャンクは最高スコアのみ残す）
        seen: dict[str, dict] = {}
        for i, meta in enumerate(results["metadatas"][0]):
            source = meta.get("source_file", "")
            similarity = round(1.0 - results["distances"][0][i], 4)
            if source not in seen or similarity > seen[source]["similarity"]:
                seen[source] = {"meta": meta, "similarity": similarity}

        # スコア順にソートしてtop_k件
        ranked = sorted(seen.values(), key=lambda x: x["similarity"], reverse=True)[:top_k]

        docs = []
        for rank, item in enumerate(ranked, 1):
            meta = item["meta"]
            source_path = Path(meta.get("source_file", ""))
            try:
                content = source_path.read_text(encoding="utf-8")
            except Exception as e:
                logger.warning("Failed to read doc %s: %s", source_path, e)
                content = ""

            docs.append({
                "rank": rank,
                "source_file": str(source_path),
                "filename": meta.get("filename", source_path.name),
                "title": meta.get("title", source_path.stem),
                "content": content,
                "url": meta.get("url", ""),
                "similarity": item["similarity"],
            })

        return docs

    def format_output(self, docs: list[dict]) -> str:
        """ターミナル表示用フォーマット"""
        if not docs:
            return "該当するドキュメントが見つかりませんでした。"

        lines = [f"=== 関連ドキュメント Top {len(docs)} ===\n"]
        for d in docs:
            lines.append(
                f"[{d['rank']}] {d['title']}\n"
                f"    ファイル: {d['filename']}  スコア: {d['similarity']:.4f}\n"
                f"    URL: {d['url']}\n"
            )
        return "\n".join(lines)
