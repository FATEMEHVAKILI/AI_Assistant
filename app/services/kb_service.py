import os
import glob
import logging
from ..config import settings
import chromadb

logger = logging.getLogger("ai_assistant")


class KBService:
    def __init__(self):
        logger.info("Initializing ChromaDB and loading Knowledge Base...")
        try:
            self.client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
            self.collection = self.client.get_or_create_collection(
                name="rastad_knowledge_base"
            )
            self._load_documents()
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.collection = None

    def _load_documents(self):
        """Load knowledge base documents if collection is empty"""
        if self.collection is None:
            return

        try:
            if self.collection.count() == 0:
                docs, metadatas, ids = [], [], []
                kb_path = settings.KB_DIR

                if not os.path.exists(kb_path):
                    logger.warning(
                        f"Knowledge base directory not found: {kb_path}")
                    return

                for idx, filepath in enumerate(glob.glob(os.path.join(kb_path, '*.txt'))):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            if content:
                                docs.append(content)
                                metadatas.append(
                                    {"source": os.path.basename(filepath)})
                                ids.append(f"doc_{idx}")
                    except Exception as e:
                        logger.warning(f"Failed to load {filepath}: {e}")

                if docs:
                    self.collection.add(
                        documents=docs,
                        metadatas=metadatas,
                        ids=ids
                    )
                    logger.info(
                        f"Successfully loaded {len(docs)} documents into ChromaDB.")
                else:
                    logger.warning(
                        "No valid documents found in knowledge base.")
            else:
                logger.info(
                    f"ChromaDB already contains {self.collection.count()} documents.")
        except Exception as e:
            logger.error(f"Error loading documents: {e}")

    def get_relevant_context(self, query: str, n_results: int = 2) -> str:
        """Get relevant context from knowledge base using vector search"""
        if self.collection is None or self.collection.count() == 0:
            logger.warning("No documents in knowledge base")
            return ""

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            if results and results.get('documents') and results['documents'][0]:
                # Join multiple relevant chunks
                context = "\n\n".join(results['documents'][0])
                logger.debug(f"Retrieved context for query: {query[:50]}...")
                return context
            return ""
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return ""
