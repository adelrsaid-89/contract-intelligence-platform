"""
FAISS query engine for Q&A operations
"""

import logging
import asyncio
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.qa_models import (
    QARequest, QAResult, QAAnswer, SourceReference, ProcessingMetadata
)
from .faiss_indexer import get_indexer
from services.extract_openai import OpenAIExtractionService
from utils.config import get_settings

logger = logging.getLogger(__name__)


class FAISSQueryEngine:
    """FAISS-based query engine for Q&A operations"""

    def __init__(self):
        self.settings = get_settings()
        self.indexer = None
        self.answer_generator = None

    async def initialize(self):
        """Initialize query engine"""
        try:
            # Get indexer
            self.indexer = await get_indexer()

            # Initialize answer generator if OpenAI is available
            if (self.settings.openai_api_key or
                (self.settings.azure_openai_api_key and self.settings.azure_openai_endpoint)):
                self.answer_generator = OpenAIExtractionService()

            logger.info("FAISS query engine initialized")

        except Exception as e:
            logger.error(f"Query engine initialization failed: {e}")
            raise

    async def query(self, request: QARequest) -> QAResult:
        """Process Q&A query"""
        start_time = time.time()

        try:
            await self._ensure_initialized()

            # Search for relevant documents
            search_results = await self._search_documents(request)

            # Generate answer
            answer = await self._generate_answer(request, search_results)

            # Create processing metadata
            processing_metadata = ProcessingMetadata(
                provider="faiss_rag",
                model=self.settings.embedding_model,
                processing_time=time.time() - start_time,
                parameters={
                    "search_mode": request.search_mode,
                    "max_results": request.max_results,
                    "confidence_threshold": request.confidence_threshold,
                    "filters": request.filters
                }
            )

            return QAResult(
                query=request.query,
                answer=answer,
                search_results_count=len(search_results),
                processing_metadata=processing_metadata,
                filters_applied=request.filters
            )

        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            raise

    async def _search_documents(self, request: QARequest) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        try:
            # Convert filters to indexer format
            indexer_filters = self._convert_filters(request.filters)

            # Perform search
            if request.search_mode == "semantic":
                results = await self.indexer.search(
                    query=request.query,
                    k=request.max_results,
                    filters=indexer_filters
                )
            elif request.search_mode == "keyword":
                results = await self._keyword_search(request.query, request.max_results, indexer_filters)
            else:  # hybrid
                semantic_results = await self.indexer.search(
                    query=request.query,
                    k=request.max_results // 2,
                    filters=indexer_filters
                )
                keyword_results = await self._keyword_search(
                    request.query, request.max_results // 2, indexer_filters
                )
                results = self._merge_results(semantic_results, keyword_results, request.max_results)

            # Filter by confidence threshold
            filtered_results = [
                result for result in results
                if result.get("score", 0) >= request.confidence_threshold
            ]

            return filtered_results

        except Exception as e:
            logger.error(f"Document search failed: {e}")
            return []

    async def _keyword_search(
        self,
        query: str,
        k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform keyword-based search"""
        try:
            # Get all documents from indexer
            # Note: This is a simplified implementation
            # For production, consider using a proper text search engine like Elasticsearch

            query_words = set(query.lower().split())
            results = []

            # Search through document store
            for index_id, metadata in self.indexer.document_store.items():
                content = metadata.get("content", "").lower()

                # Apply filters
                if filters and not self.indexer._match_filters(metadata, filters):
                    continue

                # Calculate keyword match score
                content_words = set(content.split())
                matches = query_words.intersection(content_words)
                score = len(matches) / len(query_words) if query_words else 0

                if score > 0:
                    result = {
                        "document_id": metadata["document_id"],
                        "chunk_id": metadata["chunk_id"],
                        "content": metadata["content"],
                        "title": metadata["title"],
                        "score": score,
                        "metadata": metadata["metadata"],
                        "document_type": metadata.get("document_type"),
                        "timestamp": metadata.get("timestamp")
                    }
                    results.append(result)

            # Sort by score and return top k
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:k]

        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []

    def _merge_results(
        self,
        semantic_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Merge semantic and keyword search results"""
        try:
            # Create a map to avoid duplicates
            seen_chunks = set()
            merged_results = []

            # Add semantic results first (usually higher quality)
            for result in semantic_results:
                chunk_id = result["chunk_id"]
                if chunk_id not in seen_chunks:
                    seen_chunks.add(chunk_id)
                    merged_results.append(result)

            # Add keyword results that weren't already included
            for result in keyword_results:
                chunk_id = result["chunk_id"]
                if chunk_id not in seen_chunks:
                    seen_chunks.add(chunk_id)
                    # Boost score slightly for keyword matches
                    result["score"] = result["score"] * 0.8 + 0.2
                    merged_results.append(result)

            # Sort by score and return top results
            merged_results.sort(key=lambda x: x["score"], reverse=True)
            return merged_results[:max_results]

        except Exception as e:
            logger.error(f"Results merging failed: {e}")
            return semantic_results + keyword_results

    async def _generate_answer(
        self,
        request: QARequest,
        search_results: List[Dict[str, Any]]
    ) -> QAAnswer:
        """Generate answer from search results"""
        try:
            if not search_results:
                return QAAnswer(
                    answer="I couldn't find any relevant information to answer your question.",
                    confidence=0.0,
                    answer_type="not_found",
                    sources=[],
                    related_queries=await self._get_related_queries(request.query)
                )

            # Create source references
            sources = []
            context_texts = []

            for result in search_results:
                source = SourceReference(
                    document_id=result["document_id"],
                    document_name=result.get("title", result["document_id"]),
                    document_type=result.get("document_type"),
                    text_snippet=result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"],
                    deep_link=self._create_deep_link(result),
                    relevance_score=result["score"]
                )
                sources.append(source)
                context_texts.append(result["content"])

            # Generate answer using AI if available
            if self.answer_generator and request.include_context:
                answer_text, confidence = await self._generate_ai_answer(
                    request.query, context_texts
                )
                answer_type = "synthesized"
            else:
                # Fallback: return most relevant snippet
                answer_text = search_results[0]["content"][:500]
                confidence = search_results[0]["score"]
                answer_type = "direct"

            return QAAnswer(
                answer=answer_text,
                confidence=confidence,
                answer_type=answer_type,
                sources=sources,
                related_queries=await self._get_related_queries(request.query),
                explanation=f"Answer generated from {len(sources)} relevant document(s)" if answer_type == "synthesized" else None
            )

        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            # Return fallback answer
            return QAAnswer(
                answer="An error occurred while generating the answer.",
                confidence=0.0,
                answer_type="error",
                sources=[],
                related_queries=None
            )

    async def _generate_ai_answer(self, query: str, context_texts: List[str]) -> tuple[str, float]:
        """Generate AI-powered answer from context"""
        try:
            # Combine context texts
            combined_context = "\n\n".join(context_texts[:5])  # Limit context size

            # Create prompt for answer generation
            prompt = f"""
Based on the following context documents, answer the user's question.
Provide a clear, concise answer based only on the information provided.
If the context doesn't contain enough information to answer the question, say so.

Question: {query}

Context:
{combined_context}

Answer:"""

            # Use the extraction service to generate answer
            # This is a simplified approach - in production, you might want a dedicated QA model
            client = await self.answer_generator._get_client()

            model = (self.settings.azure_openai_deployment_name
                    if hasattr(self.settings, 'azure_openai_deployment_name')
                    else self.settings.openai_model)

            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on provided context documents. Be accurate and concise."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=500
            )

            answer = response.choices[0].message.content.strip()

            # Estimate confidence based on answer content
            confidence = 0.8 if len(answer) > 20 and "don't have enough information" not in answer.lower() else 0.3

            return answer, confidence

        except Exception as e:
            logger.error(f"AI answer generation failed: {e}")
            return "Unable to generate AI answer", 0.2

    async def _get_related_queries(self, query: str) -> Optional[List[str]]:
        """Get related query suggestions"""
        try:
            # Simple related query generation based on common patterns
            # In production, you might use a more sophisticated approach

            related_patterns = {
                "obligation": [
                    "What are the deadlines for {}?",
                    "Who is responsible for {}?",
                    "What are the penalties for {}?"
                ],
                "sla": [
                    "What is the SLA for {}?",
                    "What are the performance metrics for {}?",
                    "What happens if SLA is not met for {}?"
                ],
                "payment": [
                    "What are the payment terms for {}?",
                    "When is payment due for {}?",
                    "What are the late payment penalties for {}?"
                ],
                "project": [
                    "What are the deliverables for {}?",
                    "What is the timeline for {}?",
                    "Who are the stakeholders for {}?"
                ]
            }

            # Extract key terms from query
            query_lower = query.lower()
            key_terms = [word for word in query.split() if len(word) > 3]
            context = key_terms[0] if key_terms else "this project"

            # Find matching pattern
            suggestions = []
            for pattern_type, templates in related_patterns.items():
                if pattern_type in query_lower:
                    suggestions.extend([template.format(context) for template in templates[:2]])
                    break

            if not suggestions:
                # Default suggestions
                suggestions = [
                    f"What are the obligations related to {context}?",
                    f"What are the deadlines for {context}?",
                    f"Who is responsible for {context}?"
                ]

            return suggestions[:3]

        except Exception as e:
            logger.error(f"Related queries generation failed: {e}")
            return None

    def _create_deep_link(self, result: Dict[str, Any]) -> Optional[str]:
        """Create deep link to document location"""
        try:
            document_id = result["document_id"]
            chunk_id = result["chunk_id"]

            # This would typically link to your document viewer
            # For now, return a placeholder URL
            return f"/documents/{document_id}#chunk_{chunk_id}"

        except Exception as e:
            logger.error(f"Deep link creation failed: {e}")
            return None

    def _convert_filters(self, filters: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Convert API filters to indexer filters"""
        if not filters:
            return None

        converted = {}

        # Map filter keys
        filter_mapping = {
            "project_id": "project_ids",
            "contractor": "contractors",
            "status": "statuses",
            "document_type": "document_types",
            "category": "categories",
            "confidence_min": "confidence_min",
            "date_range": "date_range"
        }

        for api_key, value in filters.items():
            indexer_key = filter_mapping.get(api_key, api_key)

            # Convert single values to lists where expected
            if indexer_key in ["project_ids", "contractors", "statuses", "document_types", "categories"]:
                if not isinstance(value, list):
                    value = [value]

            converted[indexer_key] = value

        return converted

    async def _ensure_initialized(self):
        """Ensure query engine is initialized"""
        if self.indexer is None:
            await self.initialize()


# Global query engine instance
_global_query_engine: Optional[FAISSQueryEngine] = None


async def get_query_engine() -> FAISSQueryEngine:
    """Get global query engine instance"""
    global _global_query_engine

    if _global_query_engine is None:
        _global_query_engine = FAISSQueryEngine()
        await _global_query_engine.initialize()

    return _global_query_engine