"""
OCR-specific Pydantic models
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator

from .common_models import (
    BaseResponse, DocumentInfo, ProcessingMetadata,
    TextOffset, BoundingBox, ValidationResult
)


class OCRRequest(BaseModel):
    """OCR extraction request"""
    file_path: Optional[str] = Field(None, description="Path to file in storage")
    file_url: Optional[str] = Field(None, description="URL to file")
    provider: Optional[str] = Field(None, description="OCR provider to use (local/azure)")
    languages: Optional[List[str]] = Field(None, description="Language codes for OCR")
    extract_layout: bool = Field(True, description="Whether to extract layout information")
    extract_tables: bool = Field(True, description="Whether to extract table structures")
    options: Optional[Dict[str, Any]] = Field(None, description="Provider-specific options")

    @validator('provider')
    def validate_provider(cls, v):
        if v and v not in ['local', 'azure']:
            raise ValueError('Provider must be either "local" or "azure"')
        return v

    @validator('languages')
    def validate_languages(cls, v):
        if v:
            # Common language codes validation
            valid_codes = ['eng', 'spa', 'fra', 'deu', 'ita', 'por', 'rus', 'chi_sim', 'jpn', 'kor']
            for lang in v:
                if lang not in valid_codes:
                    raise ValueError(f'Unsupported language code: {lang}')
        return v


class OCRLine(BaseModel):
    """OCR extracted line"""
    text: str = Field(..., description="Extracted text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    bounding_box: Optional[BoundingBox] = Field(None, description="Line bounding box")
    words: Optional[List[Dict[str, Any]]] = Field(None, description="Word-level details")


class OCRParagraph(BaseModel):
    """OCR extracted paragraph"""
    text: str = Field(..., description="Paragraph text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    bounding_box: Optional[BoundingBox] = Field(None, description="Paragraph bounding box")
    lines: List[OCRLine] = Field(..., description="Lines in the paragraph")


class OCRTable(BaseModel):
    """OCR extracted table"""
    row_count: int = Field(..., ge=1, description="Number of rows")
    column_count: int = Field(..., ge=1, description="Number of columns")
    cells: List[List[str]] = Field(..., description="Table cells (row x column)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Table confidence")
    bounding_box: Optional[BoundingBox] = Field(None, description="Table bounding box")


class OCRPage(BaseModel):
    """OCR extracted page"""
    page_number: int = Field(..., ge=1, description="Page number (1-indexed)")
    text: str = Field(..., description="Full page text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Page confidence")
    width: Optional[float] = Field(None, description="Page width")
    height: Optional[float] = Field(None, description="Page height")
    language: Optional[str] = Field(None, description="Detected language")
    paragraphs: List[OCRParagraph] = Field(default_factory=list, description="Extracted paragraphs")
    tables: List[OCRTable] = Field(default_factory=list, description="Extracted tables")
    rotation_angle: Optional[float] = Field(None, description="Page rotation angle")


class OCRResult(BaseModel):
    """OCR extraction result"""
    text: str = Field(..., description="Complete extracted text")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
    pages: List[OCRPage] = Field(..., description="Per-page results")
    language: Optional[str] = Field(None, description="Detected language")
    document_info: DocumentInfo = Field(..., description="Document information")
    processing_metadata: ProcessingMetadata = Field(..., description="Processing metadata")


class OCRResponse(BaseResponse):
    """OCR extraction response"""
    data: Optional[OCRResult] = Field(None, description="OCR extraction result")
    validation: Optional[ValidationResult] = Field(None, description="Input validation result")


class OCRBatchRequest(BaseModel):
    """Batch OCR request"""
    file_paths: List[str] = Field(..., min_items=1, description="List of file paths")
    provider: Optional[str] = Field(None, description="OCR provider to use")
    languages: Optional[List[str]] = Field(None, description="Language codes for OCR")
    extract_layout: bool = Field(True, description="Whether to extract layout information")
    extract_tables: bool = Field(True, description="Whether to extract table structures")
    parallel_processing: bool = Field(True, description="Process files in parallel")
    options: Optional[Dict[str, Any]] = Field(None, description="Provider-specific options")


class OCRBatchResult(BaseModel):
    """Batch OCR result"""
    results: List[OCRResult] = Field(..., description="Individual OCR results")
    total_files: int = Field(..., ge=1, description="Total number of files processed")
    successful_files: int = Field(..., ge=0, description="Number of successful extractions")
    failed_files: List[str] = Field(default_factory=list, description="List of failed file paths")
    total_processing_time: float = Field(..., ge=0, description="Total processing time")


class OCRBatchResponse(BaseResponse):
    """Batch OCR response"""
    data: Optional[OCRBatchResult] = Field(None, description="Batch OCR result")


class OCRCapabilities(BaseModel):
    """OCR provider capabilities"""
    provider: str = Field(..., description="Provider name")
    supported_formats: List[str] = Field(..., description="Supported file formats")
    supported_languages: List[str] = Field(..., description="Supported language codes")
    features: Dict[str, bool] = Field(..., description="Feature support")
    max_file_size: int = Field(..., description="Maximum file size in bytes")
    max_pages: Optional[int] = Field(None, description="Maximum number of pages")


class OCRStatus(BaseModel):
    """OCR processing status"""
    task_id: str = Field(..., description="Task identifier")
    status: str = Field(..., description="Processing status")
    progress: float = Field(..., ge=0.0, le=1.0, description="Progress percentage")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    result: Optional[OCRResult] = Field(None, description="Result if completed")