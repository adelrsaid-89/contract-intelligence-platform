"""
RAG (Retrieval-Augmented Generation) system with FAISS indexing
"""

from .faiss_indexer import FAISSIndexer, initialize_faiss_index
from .faiss_query import FAISSQueryEngine