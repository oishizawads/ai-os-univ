"""ChromaDB へのembeddingパイプライン

短いdoc（< SHORT_DOC_WORDS語）は全文を1エントリとしてembed。
長いdocはチャンク分割してembed。
"""
import logging
import re
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# この語数未満なら全文を1エントリとして扱う（≈3000トークン）
SHORT_DOC_WORDS = 1500


def _strip_frontmatter(text: str) -> str:
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        if end >= len(words):
            break
        start = end - overlap
    return chunks


class Embedder:
    def __init__(self, cfg: dict):
        embed_cfg = cfg["embedding"]
        db_cfg = cfg["database"]

        self.chunk_size = embed_cfg.get("chunk_size", 500)
        self.overlap = embed_cfg.get("chunk_overlap", 50)
        self.batch_size = embed_cfg.get("batch_size", 32)

        chroma_path = Path(db_cfg["chroma_dir"])
        chroma_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(chroma_path),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=db_cfg.get("collection_name", "knowledge_base"),
            metadata={"hnsw:space": "cosine"},
        )

        logger.info("Loading embedding model: %s", embed_cfg["model"])
        self.model = SentenceTransformer(embed_cfg["model"])
        logger.info("Embedding model ready")

    def embed_file(self, filepath: Path, article: dict) -> int:
        """Markdownファイルをembeddingして保存。追加したエントリ数を返す"""
        text = filepath.read_text(encoding="utf-8")
        body = _strip_frontmatter(text)
        if not body.strip():
            return 0

        source_id = str(filepath)

        # 既登録チェック
        existing = self.collection.get(where={"source_file": source_id}, limit=1)
        if existing["ids"]:
            logger.debug("Already embedded, skip: %s", filepath.name)
            return 0

        words = body.split()
        if len(words) < SHORT_DOC_WORDS:
            # 短いdoc: 全文を1エントリ
            entries = [(f"{filepath.stem}_full", body)]
            logger.debug("Short doc, embedding full text (%d words): %s", len(words), filepath.name)
        else:
            # 長いdoc: チャンク分割
            chunks = _chunk_text(body, self.chunk_size, self.overlap)
            entries = [(f"{filepath.stem}_chunk{i}", chunk) for i, chunk in enumerate(chunks)]
            logger.debug("Long doc, embedding %d chunks (%d words): %s", len(entries), len(words), filepath.name)

        base_meta = {
            "source_file": source_id,
            "filename": filepath.name,
            "title": article.get("title", filepath.stem),
            "type": article.get("type", filepath.parent.name),
            "published": article.get("published", ""),
            "url": article.get("url", ""),
            "is_full_doc": len(words) < SHORT_DOC_WORDS,
        }

        ids, embeddings, metadatas, documents = [], [], [], []
        for entry_id, content in entries:
            emb = self.model.encode(content, normalize_embeddings=True).tolist()
            ids.append(entry_id)
            embeddings.append(emb)
            metadatas.append({**base_meta})
            documents.append(content)

        for batch_start in range(0, len(ids), self.batch_size):
            sl = slice(batch_start, batch_start + self.batch_size)
            self.collection.add(
                ids=ids[sl],
                embeddings=embeddings[sl],
                metadatas=metadatas[sl],
                documents=documents[sl],
            )

        logger.info("Embedded %d entries: %s", len(entries), filepath.name)
        return len(entries)

    def embed_vault(self, vault_cfg: dict) -> int:
        """Vault内の全Markdownを再スキャンしてembedding（未登録分のみ）"""
        vault_root = Path(vault_cfg["path"])
        total = 0
        for md_file in vault_root.rglob("*.md"):
            if md_file.parent.name in ("_templates",):
                continue
            article = {"title": md_file.stem, "type": md_file.parent.name}
            total += self.embed_file(md_file, article)

        # extra_knowledge_dirs（ai-os/knowledge/ 等）も登録
        for extra_dir_str in vault_cfg.get("extra_knowledge_dirs", []):
            extra_dir = Path(extra_dir_str)
            if not extra_dir.exists():
                logger.warning("extra_knowledge_dir not found, skip: %s", extra_dir)
                continue
            for md_file in extra_dir.rglob("*.md"):
                if md_file.name.startswith("_"):
                    continue
                article = {"title": md_file.stem, "type": md_file.parent.name}
                total += self.embed_file(md_file, article)

        return total
