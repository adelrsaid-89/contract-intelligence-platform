"""
Common Pydantic models used across the AI Operations Microservice
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConfidenceScore(BaseModel):
    """Confidence score model"""
    value: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    source: str = Field(..., description="Source of the confidence score")


class TextOffset(BaseModel):
    """Text offset model for tracking location in documents"""
    start: int = Field(..., ge=0, description="Start character position")
    end: int = Field(..., ge=0, description="End character position")
    page: Optional[int] = Field(None, ge=1, description="Page number (1-indexed)")
    line: Optional[int] = Field(None, ge=1, description="Line number (1-indexed)")


class BoundingBox(BaseModel):
    """Bounding box for layout information"""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    width: float = Field(..., description="Width")
    height: float = Field(..., description="Height")
    page: Optional[int] = Field(None, ge=1, description="Page number (1-indexed)")


class ExtractedField(BaseModel):
    """Base model for extracted fields"""
    value: str = Field(..., description="Extracted value")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    text_offset: Optional[TextOffset] = Field(None, description="Location in source text")
    bounding_box: Optional[BoundingBox] = Field(None, description="Visual location")
    source: str = Field(..., description="Extraction source/method")


class DocumentInfo(BaseModel):
    """Document information model"""
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    page_count: Optional[int] = Field(None, ge=1, description="Number of pages")
    language: Optional[str] = Field(None, description="Detected language")
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)


class ProcessingMetadata(BaseModel):
    """Processing metadata"""
    provider: str = Field(..., description="Processing provider used")
    model: Optional[str] = Field(None, description="Model name/version")
    processing_time: float = Field(..., ge=0, description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    parameters: Optional[Dict[str, Any]] = Field(None, description="Processing parameters")


class ValidationResult(BaseModel):
    """Validation result model"""
    is_valid: bool = Field(..., description="Whether the input is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")


class PaginatedResponse(BaseModel):
    """Paginated response model"""
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, description="Items per page")
    total_pages: int = Field(..., ge=1, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")


class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    dependencies: Optional[Dict[str, str]] = Field(None, description="Dependency status")


class ProvidersResponse(BaseModel):
    """Providers configuration response"""
    ocr_provider: str = Field(..., description="Active OCR provider")
    extract_provider: str = Field(..., description="Active extraction provider")
    available_providers: Dict[str, List[str]] = Field(..., description="Available providers")
    features: Dict[str, bool] = Field(..., description="Feature availability")