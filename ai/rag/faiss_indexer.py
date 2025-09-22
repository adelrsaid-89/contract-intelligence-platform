"""
FAISS indexer for building and managing vector indices
"""

import os
import pickle
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import time

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from utils.config import get_settings

logger = logging.getLogger(__name__)


class FAISSIndexer:
    """FAISS indexer for document embeddings"""

    def __init__(self, index_path: Optional[str] = None, embedding_model: Optional[str] = None):
        self.settings = get_settings()
        self.index_path = Path(index_path or self.settings.faiss_index_path)
        self.embedding_model_name = embedding_model or self.settings.embedding_model

        self.embedding_model = None
        self.index = None
        self.document_store = {}  # document_id -> document metadata
        self.embedding_dimension = 384  # Default for all-MiniLM-L6-v2

        self._initialized = False

    async def initialize(self):
        """Initialize the indexer"""
        if self._initialized:
            return

        try:
            logger.info(f"Initializing FAISS indexer with model: {self.embedding_model_name}")

            # Create index directory
            self.index_path.mkdir(parents=True, exist_ok=True)

            # Load embedding model
            loop = asyncio.get_event_loop()
            self.embedding_model = await loop.run_in_executor(
                None, lambda: SentenceTransformer(self.embedding_model_name)
            )

            # Get actual embedding dimension
            test_embedding = await self._embed_text("test")
            self.embedding_dimension = len(test_embedding)

            # Load existing index if available
            await self._load_index()

            self._initialized = True
            logger.info("FAISS indexer initialized successfully")

        except Exception as e:
            logger.error(f"FAISS indexer initialization failed: {e}")
            raise

    async def _embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        if not self.embedding_model:
            raise RuntimeError("Embedding model not initialized")

        try:
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, lambda: self.embedding_model.encode(text, convert_to_numpy=True)
            )
            return embedding.astype(np.float32)

        except Exception as e:
            logger.error(f"Text embedding failed: {e}")
            raise

    async def _embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        if not self.embedding_model:
            raise RuntimeError("Embedding model not initialized")

        try:
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None, lambda: self.embedding_model.encode(texts, convert_to_numpy=True)
            )
            return embeddings.astype(np.float32)

        except Exception as e:
            logger.error(f"Batch text embedding failed: {e}")
            raise

    async def add_documents(self, documents: List[Dict[str, Any]]) -> int:
        """Add documents to the index"""
        await self._ensure_initialized()

        if not documents:
            return 0

        try:
            logger.info(f"Adding {len(documents)} documents to index")
            start_time = time.time()

            # Prepare embeddings
            texts_to_embed = []
            document_metadata = []

            for doc in documents:
                document_id = doc.get("document_id")
                content = doc.get("content", "")

                if not document_id or not content:
                    logger.warning(f"Skipping document with missing ID or content: {doc}")
                    continue

                # Split content into chunks if too long
                chunks = self._chunk_text(content)

                for i, chunk in enumerate(chunks):
                    chunk_id = f"{document_id}_chunk_{i}" if len(chunks) > 1 else document_id
                    texts_to_embed.append(chunk)

                    # Store metadata for each chunk
                    chunk_metadata = {
                        "document_id": document_id,
                        "chunk_id": chunk_id,
                        "chunk_index": i,
                        "content": chunk,
                        "title": doc.get("title", ""),
                        "metadata": doc.get("metadata", {}),
                        "document_type": doc.get("document_type"),
                        "timestamp": doc.get("timestamp")
                    }
                    document_metadata.append(chunk_metadata)

            if not texts_to_embed:
                logger.warning("No valid texts to embed")
                return 0

            # Generate embeddings
            embeddings = await self._embed_texts(texts_to_embed)

            # Initialize index if needed
            if self.index is None:
                self.index = faiss.IndexFlatIP(self.embedding_dimension)  # Inner product for cosine similarity

            # Add to index
            loop = asyncio.get_event_loop()
            start_index = self.index.ntotal

            await loop.run_in_executor(
                None, lambda: self.index.add(embeddings)
            )

            # Update document store
            for i, metadata in enumerate(document_metadata):
                index_id = start_index + i
                self.document_store[index_id] = metadata

            # Save index
            await self._save_index()

            processing_time = time.time() - start_time
            logger.info(f"Added {len(texts_to_embed)} chunks to index in {processing_time:.2f}s")

            return len(texts_to_embed)

        except Exception as e:
            logger.error(f"Document addition failed: {e}")
            raise

    async def search(
        self,
        query: str,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search the index"""
        await self._ensure_initialized()

        if self.index is None or self.index.ntotal == 0:
            logger.warning("Index is empty")
            return []

        try:
            # Generate query embedding
            query_embedding = await self._embed_text(query)
            query_embedding = query_embedding.reshape(1, -1)

            # Normalize for cosine similarity
            faiss.normalize_L2(query_embedding)

            # Search
            loop = asyncio.get_event_loop()
            search_k = min(k * 2, self.index.ntotal)  # Get more results for filtering

            scores, indices = await loop.run_in_executor(
                None, lambda: self.index.search(query_embedding, search_k)
            )

            # Process results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # Invalid index
                    continue

                document_metadata = self.document_store.get(idx)
                if not document_metadata:
                    continue

                # Apply filters
                if filters and not self._match_filters(document_metadata, filters):
                    continue

                result = {
                    "document_id": document_metadata["document_id"],
                    "chunk_id": document_metadata["chunk_id"],
                    "content": document_metadata["content"],
                    "title": document_metadata["title"],
                    "score": float(score),
                    "metadata": document_metadata["metadata"],
                    "document_type": document_metadata.get("document_type"),
                    "timestamp": document_metadata.get("timestamp")
                }
                results.append(result)

                if len(results) >= k:
                    break

            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    async def delete_documents(self, document_ids: List[str]) -> int:
        """Delete documents from index"""
        await self._ensure_initialized()

        if self.index is None:
            return 0

        try:
            # Find indices to remove
            indices_to_remove = []
            for index_id, metadata in self.document_store.items():
                if metadata["document_id"] in document_ids:
                    indices_to_remove.append(index_id)

            if not indices_to_remove:
                return 0

            # Note: FAISS doesn't support efficient deletion
            # For production, consider using a different approach or rebuilding the index
            logger.warning("FAISS doesn't support efficient deletion. Consider rebuilding index.")

            # Mark as deleted in document store
            deleted_count = 0
            for index_id in indices_to_remove:
                if index_id in self.document_store:
                    del self.document_store[index_id]
                    deleted_count += 1

            # Save updated document store
            await self._save_document_store()

            return deleted_count

        except Exception as e:
            logger.error(f"Document deletion failed: {e}")
            raise

    async def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        await self._ensure_initialized()

        total_vectors = self.index.ntotal if self.index else 0
        active_documents = len(set(
            metadata["document_id"]
            for metadata in self.document_store.values()
        ))

        return {
            "total_vectors": total_vectors,
            "active_documents": active_documents,
            "total_chunks": len(self.document_store),
            "embedding_dimension": self.embedding_dimension,
            "index_size_bytes": self._get_index_size(),
            "model": self.embedding_model_name
        }

    def _chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                chunk_text = text[start:end]
                last_sentence_end = max(
                    chunk_text.rfind('.'),
                    chunk_text.rfind('!'),
                    chunk_text.rfind('?')
                )

                if last_sentence_end > chunk_size * 0.5:  # Only if we found a reasonable break
                    end = start + last_sentence_end + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start with overlap
            start = end - overlap
            if start >= len(text):
                break

        return chunks

    def _match_filters(self, document_metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if document matches filters"""
        try:
            metadata = document_metadata.get("metadata", {})

            for filter_key, filter_value in filters.items():
                if filter_key == "project_ids":
                    project_id = metadata.get("project_id")
                    if project_id not in filter_value:
                        return False

                elif filter_key == "contractors":
                    contractor = metadata.get("contractor")
                    if contractor not in filter_value:
                        return False

                elif filter_key == "statuses":
                    status = metadata.get("status")
                    if status not in filter_value:
                        return False

                elif filter_key == "document_types":
                    doc_type = document_metadata.get("document_type")
                    if doc_type not in filter_value:
                        return False

                elif filter_key == "categories":
                    category = metadata.get("category")
                    if category not in filter_value:
                        return False

                elif filter_key == "confidence_min":
                    confidence = metadata.get("confidence", 1.0)
                    if confidence < filter_value:
                        return False

                elif filter_key == "date_range":
                    timestamp = document_metadata.get("timestamp")
                    if timestamp:
                        if "start" in filter_value and timestamp < filter_value["start"]:
                            return False
                        if "end" in filter_value and timestamp > filter_value["end"]:
                            return False

            return True

        except Exception as e:
            logger.error(f"Filter matching failed: {e}")
            return False

    async def _load_index(self):
        """Load existing index from disk"""
        try:
            index_file = self.index_path / "faiss.index"
            store_file = self.index_path / "document_store.pkl"

            if index_file.exists() and store_file.exists():
                logger.info("Loading existing FAISS index")

                # Load index
                loop = asyncio.get_event_loop()
                self.index = await loop.run_in_executor(
                    None, lambda: faiss.read_index(str(index_file))
                )

                # Load document store
                with open(store_file, 'rb') as f:
                    self.document_store = pickle.load(f)

                logger.info(f"Loaded index with {self.index.ntotal} vectors")

            else:
                logger.info("No existing index found, will create new one")
                self.index = None
                self.document_store = {}

        except Exception as e:
            logger.error(f"Index loading failed: {e}")
            # Reset to empty state
            self.index = None
            self.document_store = {}

    async def _save_index(self):
        """Save index to disk"""
        try:
            if self.index is None:
                return

            index_file = self.index_path / "faiss.index"
            store_file = self.index_path / "document_store.pkl"

            # Save index
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, lambda: faiss.write_index(self.index, str(index_file))
            )

            # Save document store
            await self._save_document_store()

        except Exception as e:
            logger.error(f"Index saving failed: {e}")

    async def _save_document_store(self):
        """Save document store to disk"""
        try:
            store_file = self.index_path / "document_store.pkl"

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._write_pickle(store_file, self.document_store)
            )

        except Exception as e:
            logger.error(f"Document store saving failed: {e}")

    def _write_pickle(self, file_path: Path, data: Any):
        """Write data to pickle file"""
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)

    def _get_index_size(self) -> int:
        """Get approximate index size in bytes"""
        try:
            index_file = self.index_path / "faiss.index"
            store_file = self.index_path / "document_store.pkl"

            size = 0
            if index_file.exists():
                size += index_file.stat().st_size
            if store_file.exists():
                size += store_file.stat().st_size

            return size

        except Exception:
            return 0

    async def _ensure_initialized(self):
        """Ensure indexer is initialized"""
        if not self._initialized:
            await self.initialize()


# Global indexer instance
_global_indexer: Optional[FAISSIndexer] = None


async def get_indexer() -> FAISSIndexer:
    """Get global indexer instance"""
    global _global_indexer

    if _global_indexer is None:
        _global_indexer = FAISSIndexer()
        await _global_indexer.initialize()

    return _global_indexer


async def initialize_faiss_index():
    """Initialize global FAISS index"""
    try:
        indexer = await get_indexer()
        logger.info("Global FAISS index initialized")
        return indexer
    except Exception as e:
        logger.error(f"Global FAISS index initialization failed: {e}")
        raise