import os
import glob
import logging

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("CHROMA_TELEMETRY", "False")

import chromadb
from chromadb.config import Settings as ChromaSettings
from ..config import settings

logger = logging.getLogger("ai_assistant")


class KBService:
    def __init__(self):
        logger.info("Initializing ChromaDB and loading Knowledge Base...")
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DIR,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                chroma_product_telemetry_impl="app.services.chroma_telemetry.NoopTelemetry",
                chroma_telemetry_impl="app.services.chroma_telemetry.NoopTelemetry",
            ),
        )
        self.collection = self.client.get_or_create_collection(
            name="ai_assistant_kb")
        self._load_documents()

    def _load_documents(self):
        if self.collection.count() == 0:
            docs, metadatas, ids = [], [], []
            for idx, filepath in enumerate(glob.glob(os.path.join(settings.KB_DIR, '*.txt'))):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        docs.append(content)
                        metadatas.append(
                            {"source": os.path.basename(filepath)})
                        ids.append(f"doc_{idx}")
            if docs:
                self.collection.add(
                    documents=docs, metadatas=metadatas, ids=ids)
                logger.info(f"Loaded {len(docs)} documents into ChromaDB.")
        else:
            logger.info(
                f"ChromaDB already contains {self.collection.count()} documents.")

    def search(self, query: str, n_results=1):
        if self.collection.count() == 0:
            return None
        results = self.collection.query(
            query_texts=[query], n_results=n_results)
        if results['documents'] and results['documents'][0]:
            return results['documents'][0][0]
        return None
