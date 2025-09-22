"""
Q&A RAG system Pydantic models
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator

from .common_models import (
    BaseResponse, ProcessingMetadata, PaginatedResponse,
    ConfidenceScore, ValidationResult
)


class QARequest(BaseModel):
    """Q&A query request"""
    query: str = Field(..., min_length=3, max_length=1000, description="Natural language query")
    filters: Optional[Dict[str, Any]] = Field(None, description="Query filters")
    max_results: int = Field(10, ge=1, le=100, description="Maximum number of results")
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")
    include_context: bool = Field(True, description="Include source context in response")
    search_mode: str = Field("hybrid", description="Search mode (semantic/keyword/hybrid)")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional query options")

    @validator('search_mode')
    def validate_search_mode(cls, v):
        if v not in ['semantic', 'keyword', 'hybrid']:
            raise ValueError('Search mode must be one of: semantic, keyword, hybrid')
        return v

    @validator('filters')
    def validate_filters(cls, v):
        if v:
            # Validate filter keys
            valid_filter_keys = [
                'project_id', 'contractor', 'status', 'date_range',
                'document_type', 'category', 'confidence_min'
            ]
            for key in v.keys():
                if key not in valid_filter_keys:
                    raise ValueError(f'Invalid filter key: {key}')
        return v


class SourceReference(BaseModel):
    """Reference to source document/clause"""
    document_id: str = Field(..., description="Document identifier")
    document_name: str = Field(..., description="Document name")
    document_type: Optional[str] = Field(None, description="Document type")
    page_number: Optional[int] = Field(None, ge=1, description="Page number")
    section: Optional[str] = Field(None, description="Section/clause identifier")
    text_snippet: str = Field(..., description="Relevant text snippet")
    deep_link: Optional[str] = Field(None, description="Deep link to specific location")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance to query")


class QAAnswer(BaseModel):
    """Q&A answer"""
    answer: str = Field(..., description="Generated answer")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Answer confidence score")
    answer_type: str = Field(..., description="Type of answer (direct/synthesized/not_found)")
    sources: List[SourceReference] = Field(..., description="Source references")
    related_queries: Optional[List[str]] = Field(None, description="Related query suggestions")
    explanation: Optional[str] = Field(None, description="Explanation of how answer was derived")


class QAResult(BaseModel):
    """Q&A query result"""
    query: str = Field(..., description="Original query")
    answer: QAAnswer = Field(..., description="Generated answer")
    search_results_count: int = Field(..., ge=0, description="Number of search results found")
    processing_metadata: ProcessingMetadata = Field(..., description="Processing metadata")
    filters_applied: Optional[Dict[str, Any]] = Field(None, description="Filters that were applied")


class QAResponse(BaseResponse):
    """Q&A query response"""
    data: Optional[QAResult] = Field(None, description="Q&A result")
    validation: Optional[ValidationResult] = Field(None, description="Input validation result")


class QABatchRequest(BaseModel):
    """Batch Q&A request"""
    queries: List[str] = Field(..., min_items=1, max_items=50, description="List of queries")
    filters: Optional[Dict[str, Any]] = Field(None, description="Common filters for all queries")
    max_results_per_query: int = Field(10, ge=1, le=50, description="Max results per query")
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")
    parallel_processing: bool = Field(True, description="Process queries in parallel")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional options")


class QABatchResult(BaseModel):
    """Batch Q&A result"""
    results: List[QAResult] = Field(..., description="Individual Q&A results")
    total_queries: int = Field(..., ge=1, description="Total number of queries processed")
    successful_queries: int = Field(..., ge=0, description="Number of successful queries")
    failed_queries: List[str] = Field(default_factory=list, description="List of failed queries")
    total_processing_time: float = Field(..., ge=0, description="Total processing time")
    average_confidence: float = Field(..., ge=0.0, le=1.0, description="Average confidence across all results")


class QABatchResponse(BaseResponse):
    """Batch Q&A response"""
    data: Optional[QABatchResult] = Field(None, description="Batch Q&A result")


class IndexDocument(BaseModel):
    """Document to be indexed"""
    document_id: str = Field(..., description="Unique document identifier")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")
    document_type: Optional[str] = Field(None, description="Document type")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Index timestamp")


class IndexRequest(BaseModel):
    """Index update request"""
    documents: List[IndexDocument] = Field(..., min_items=1, description="Documents to index")
    operation: str = Field("upsert", description="Index operation (upsert/delete)")
    batch_size: int = Field(100, ge=1, le=1000, description="Batch size for processing")
    options: Optional[Dict[str, Any]] = Field(None, description="Indexing options")

    @validator('operation')
    def validate_operation(cls, v):
        if v not in ['upsert', 'delete', 'update']:
            raise ValueError('Operation must be one of: upsert, delete, update')
        return v


class IndexResult(BaseModel):
    """Index update result"""
    indexed_documents: int = Field(..., ge=0, description="Number of documents indexed")
    failed_documents: List[str] = Field(default_factory=list, description="Failed document IDs")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")
    index_size: Optional[int] = Field(None, description="Total index size after operation")


class IndexResponse(BaseResponse):
    """Index update response"""
    data: Optional[IndexResult] = Field(None, description="Index result")


class SearchFilters(BaseModel):
    """Search filters for Q&A"""
    project_ids: Optional[List[str]] = Field(None, description="Filter by project IDs")
    contractors: Optional[List[str]] = Field(None, description="Filter by contractors")
    statuses: Optional[List[str]] = Field(None, description="Filter by status")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range filter")
    document_types: Optional[List[str]] = Field(None, description="Filter by document types")
    categories: Optional[List[str]] = Field(None, description="Filter by categories")
    confidence_min: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum confidence filter")


class QuerySuggestion(BaseModel):
    """Query suggestion"""
    query: str = Field(..., description="Suggested query")
    category: str = Field(..., description="Query category")
    description: Optional[str] = Field(None, description="Query description")
    expected_answer_type: Optional[str] = Field(None, description="Expected answer type")


class QASuggestions(BaseModel):
    """Q&A query suggestions"""
    suggestions: List[QuerySuggestion] = Field(..., description="Query suggestions")
    categories: List[str] = Field(..., description="Available categories")


class QACapabilities(BaseModel):
    """Q&A system capabilities"""
    supported_search_modes: List[str] = Field(..., description="Supported search modes")
    supported_filters: List[str] = Field(..., description="Supported filter types")
    max_query_length: int = Field(..., description="Maximum query length")
    max_results: int = Field(..., description="Maximum results per query")
    supported_document_types: List[str] = Field(..., description="Supported document types")
    index_size: int = Field(..., description="Current index size")
    features: Dict[str, bool] = Field(..., description="Feature availability")


class QAMetrics(BaseModel):
    """Q&A system metrics"""
    total_queries: int = Field(..., description="Total queries processed")
    average_response_time: float = Field(..., description="Average response time")
    average_confidence: float = Field(..., description="Average confidence score")
    most_common_queries: List[str] = Field(..., description="Most common query patterns")
    index_health: Dict[str, Any] = Field(..., description="Index health metrics")
    performance_stats: Dict[str, float] = Field(..., description="Performance statistics")