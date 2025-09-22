"""
Q&A RAG system API router
"""

import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse

from models.qa_models import (
    QARequest, QAResponse, QABatchRequest, QABatchResponse,
    IndexRequest, IndexResponse, QACapabilities, QAMetrics,
    QASuggestions, ValidationResult
)
from models.common_models import ErrorResponse
from rag.faiss_query import get_query_engine
from rag.faiss_indexer import get_indexer
from utils.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/query", response_model=QAResponse)
async def query_documents(
    request: QARequest,
    background_tasks: BackgroundTasks
):
    """
    Query documents using natural language Q&A

    - **query**: Natural language question
    - **filters**: Optional filters (project_id, contractor, status, etc.)
    - **max_results**: Maximum number of results to return
    - **confidence_threshold**: Minimum confidence threshold
    - **include_context**: Include source context in response
    - **search_mode**: Search mode (semantic/keyword/hybrid)
    """
    try:
        # Validate request
        validation = await validate_qa_request(request)
        if not validation.is_valid:
            return QAResponse(
                success=False,
                message="Invalid request",
                validation=validation
            )

        # Get query engine
        query_engine = await get_query_engine()

        # Process query
        try:
            result = await query_engine.query(request)

            return QAResponse(
                success=True,
                message="Query processed successfully",
                data=result,
                validation=validation
            )

        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Q&A endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/batch-query", response_model=QABatchResponse)
async def batch_query_documents(
    request: QABatchRequest,
    background_tasks: BackgroundTasks
):
    """
    Process multiple queries in batch

    - **queries**: List of natural language questions
    - **filters**: Common filters for all queries
    - **max_results_per_query**: Maximum results per individual query
    - **confidence_threshold**: Minimum confidence threshold
    - **parallel_processing**: Process queries in parallel
    """
    try:
        # Validate request
        if not request.queries:
            raise HTTPException(status_code=400, detail="queries cannot be empty")

        if len(request.queries) > 50:
            raise HTTPException(status_code=400, detail="Maximum 50 queries per batch")

        # Get query engine
        query_engine = await get_query_engine()

        # Process queries
        import asyncio
        import time

        start_time = time.time()
        results = []
        failed_queries = []

        try:
            if request.parallel_processing:
                # Process in parallel
                tasks = []
                for query in request.queries:
                    individual_request = QARequest(
                        query=query,
                        filters=request.filters,
                        max_results=request.max_results_per_query,
                        confidence_threshold=request.confidence_threshold,
                        options=request.options
                    )
                    task = query_engine.query(individual_request)
                    tasks.append(task)

                completed_results = await asyncio.gather(*tasks, return_exceptions=True)

                for i, result in enumerate(completed_results):
                    if isinstance(result, Exception):
                        failed_queries.append(request.queries[i])
                        logger.error(f"Failed to process query '{request.queries[i]}': {result}")
                    else:
                        results.append(result)

            else:
                # Process sequentially
                for query in request.queries:
                    try:
                        individual_request = QARequest(
                            query=query,
                            filters=request.filters,
                            max_results=request.max_results_per_query,
                            confidence_threshold=request.confidence_threshold,
                            options=request.options
                        )
                        result = await query_engine.query(individual_request)
                        results.append(result)
                    except Exception as e:
                        failed_queries.append(query)
                        logger.error(f"Failed to process query '{query}': {e}")

            total_processing_time = time.time() - start_time

            # Calculate average confidence
            all_confidences = [r.answer.confidence for r in results]
            average_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0

            from models.qa_models import QABatchResult
            batch_result = QABatchResult(
                results=results,
                total_queries=len(request.queries),
                successful_queries=len(results),
                failed_queries=failed_queries,
                total_processing_time=total_processing_time,
                average_confidence=average_confidence
            )

            return QABatchResponse(
                success=True,
                message=f"Processed {len(results)}/{len(request.queries)} queries successfully",
                data=batch_result
            )

        except Exception as e:
            logger.error(f"Batch query processing failed: {e}")
            raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch Q&A endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/index", response_model=IndexResponse)
async def update_index(
    request: IndexRequest,
    background_tasks: BackgroundTasks
):
    """
    Update the search index with new documents

    - **documents**: List of documents to index
    - **operation**: Index operation (upsert/delete/update)
    - **batch_size**: Batch size for processing
    """
    try:
        # Validate request
        if not request.documents:
            raise HTTPException(status_code=400, detail="documents cannot be empty")

        if len(request.documents) > 1000:
            raise HTTPException(status_code=400, detail="Maximum 1000 documents per request")

        # Get indexer
        indexer = await get_indexer()

        # Process based on operation
        try:
            if request.operation == "upsert":
                # Convert to indexer format
                documents_to_index = []
                for doc in request.documents:
                    index_doc = {
                        "document_id": doc.document_id,
                        "title": doc.title,
                        "content": doc.content,
                        "metadata": doc.metadata,
                        "document_type": doc.document_type,
                        "timestamp": doc.timestamp
                    }
                    documents_to_index.append(index_doc)

                indexed_count = await indexer.add_documents(documents_to_index)

                from models.qa_models import IndexResult
                result = IndexResult(
                    indexed_documents=indexed_count,
                    failed_documents=[],
                    processing_time=0.0,  # Will be updated by indexer
                    index_size=(await indexer.get_index_stats())["total_vectors"]
                )

            elif request.operation == "delete":
                document_ids = [doc.document_id for doc in request.documents]
                deleted_count = await indexer.delete_documents(document_ids)

                from models.qa_models import IndexResult
                result = IndexResult(
                    indexed_documents=0,
                    failed_documents=[],
                    processing_time=0.0,
                    index_size=(await indexer.get_index_stats())["total_vectors"]
                )

            else:
                raise HTTPException(status_code=400, detail=f"Unsupported operation: {request.operation}")

            return IndexResponse(
                success=True,
                message=f"Index {request.operation} completed successfully",
                data=result
            )

        except Exception as e:
            logger.error(f"Index operation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Index operation failed: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Index endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/suggestions", response_model=QASuggestions)
async def get_query_suggestions():
    """Get suggested queries and categories"""
    try:
        suggestions = [
            {
                "query": "What obligations are due this month for project ABC?",
                "category": "obligations",
                "description": "Find obligations with deadlines in the current month",
                "expected_answer_type": "list"
            },
            {
                "query": "What is the SLA for water spillage in project XYZ?",
                "category": "sla",
                "description": "Find specific service level agreements",
                "expected_answer_type": "direct"
            },
            {
                "query": "What are the common obligations between project A and project B?",
                "category": "comparison",
                "description": "Compare obligations across projects",
                "expected_answer_type": "comparison"
            },
            {
                "query": "Which obligations are overdue and linked to subcontractors?",
                "category": "status",
                "description": "Find overdue obligations by contractor type",
                "expected_answer_type": "filtered_list"
            },
            {
                "query": "What are the penalty clauses for late deliveries?",
                "category": "penalties",
                "description": "Find penalty information for specific scenarios",
                "expected_answer_type": "direct"
            },
            {
                "query": "Who is responsible for maintenance obligations in project DEF?",
                "category": "responsibility",
                "description": "Find responsible parties for specific obligation types",
                "expected_answer_type": "direct"
            }
        ]

        categories = ["obligations", "sla", "penalties", "comparison", "status", "responsibility", "general"]

        from models.qa_models import QuerySuggestion
        suggestion_objects = [QuerySuggestion(**s) for s in suggestions]

        return QASuggestions(
            suggestions=suggestion_objects,
            categories=categories
        )

    except Exception as e:
        logger.error(f"Suggestions endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get suggestions")


@router.get("/capabilities", response_model=QACapabilities)
async def get_qa_capabilities():
    """Get Q&A system capabilities"""
    try:
        indexer = await get_indexer()
        stats = await indexer.get_index_stats()

        capabilities = QACapabilities(
            supported_search_modes=["semantic", "keyword", "hybrid"],
            supported_filters=["project_id", "contractor", "status", "document_type", "category", "date_range"],
            max_query_length=1000,
            max_results=100,
            supported_document_types=["contract", "sla", "obligation", "report", "general"],
            index_size=stats["total_vectors"],
            features={
                "semantic_search": True,
                "keyword_search": True,
                "hybrid_search": True,
                "filtering": True,
                "confidence_scoring": True,
                "source_references": True,
                "deep_links": True,
                "batch_processing": True,
                "related_queries": True,
                "answer_generation": True
            }
        )

        return capabilities

    except Exception as e:
        logger.error(f"Capabilities endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get capabilities")


@router.get("/metrics", response_model=QAMetrics)
async def get_qa_metrics():
    """Get Q&A system performance metrics"""
    try:
        indexer = await get_indexer()
        stats = await indexer.get_index_stats()

        # In a real implementation, you'd track these metrics over time
        metrics = QAMetrics(
            total_queries=0,  # Would be tracked in database
            average_response_time=1.2,  # Would be calculated from logs
            average_confidence=0.75,  # Would be calculated from query results
            most_common_queries=[
                "What are the obligations for this project?",
                "What is the SLA for this service?",
                "What are the penalty clauses?"
            ],
            index_health={
                "total_documents": stats["active_documents"],
                "total_vectors": stats["total_vectors"],
                "index_size_mb": stats["index_size_bytes"] / (1024 * 1024),
                "last_updated": "2024-01-01T00:00:00Z"  # Would be actual timestamp
            },
            performance_stats={
                "avg_search_time_ms": 150.0,
                "avg_answer_generation_time_ms": 800.0,
                "cache_hit_rate": 0.85,
                "error_rate": 0.02
            }
        )

        return metrics

    except Exception as e:
        logger.error(f"Metrics endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")


@router.get("/search-preview")
async def search_preview(
    query: str = Query(..., description="Search query"),
    max_results: int = Query(5, ge=1, le=20, description="Maximum results"),
    search_mode: str = Query("semantic", description="Search mode")
):
    """
    Preview search results without full Q&A processing
    """
    try:
        # Get indexer for direct search
        indexer = await get_indexer()

        # Perform search
        results = await indexer.search(
            query=query,
            k=max_results
        )

        # Format results
        preview_results = []
        for result in results:
            preview_results.append({
                "document_id": result["document_id"],
                "title": result["title"],
                "snippet": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"],
                "score": result["score"],
                "document_type": result.get("document_type"),
                "metadata": result.get("metadata", {})
            })

        return {
            "success": True,
            "message": f"Found {len(preview_results)} results",
            "data": {
                "query": query,
                "results": preview_results,
                "total_results": len(preview_results),
                "search_mode": search_mode
            }
        }

    except Exception as e:
        logger.error(f"Search preview error: {e}")
        raise HTTPException(status_code=500, detail="Search preview failed")


async def validate_qa_request(request: QARequest) -> ValidationResult:
    """Validate Q&A request"""
    errors = []
    warnings = []

    try:
        # Validate query
        if not request.query or len(request.query.strip()) < 3:
            errors.append("Query must be at least 3 characters long")

        if len(request.query) > 1000:
            errors.append("Query is too long (maximum 1000 characters)")

        # Validate search mode
        if request.search_mode not in ['semantic', 'keyword', 'hybrid']:
            errors.append("Search mode must be 'semantic', 'keyword', or 'hybrid'")

        # Validate confidence threshold
        if not (0.0 <= request.confidence_threshold <= 1.0):
            errors.append("Confidence threshold must be between 0.0 and 1.0")

        # Validate max results
        if not (1 <= request.max_results <= 100):
            errors.append("Max results must be between 1 and 100")

        # Validate filters
        if request.filters:
            valid_filter_keys = [
                'project_id', 'contractor', 'status', 'date_range',
                'document_type', 'category', 'confidence_min'
            ]
            for key in request.filters.keys():
                if key not in valid_filter_keys:
                    warnings.append(f"Filter key '{key}' may not be supported")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    except Exception as e:
        logger.error(f"Request validation failed: {e}")
        return ValidationResult(
            is_valid=False,
            errors=["Request validation failed"],
            warnings=[]
        )