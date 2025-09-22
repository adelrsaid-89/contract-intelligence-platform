"""
Metadata and obligation extraction Pydantic models
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator

from .common_models import (
    BaseResponse, DocumentInfo, ProcessingMetadata,
    ExtractedField, TextOffset, BoundingBox, ValidationResult
)


class MetadataRequest(BaseModel):
    """Metadata extraction request"""
    text: Optional[str] = Field(None, description="Text to extract metadata from")
    file_path: Optional[str] = Field(None, description="Path to file in storage")
    provider: Optional[str] = Field(None, description="Extraction provider (local/openai)")
    extract_fields: Optional[List[str]] = Field(None, description="Specific fields to extract")
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")
    options: Optional[Dict[str, Any]] = Field(None, description="Provider-specific options")

    @validator('provider')
    def validate_provider(cls, v):
        if v and v not in ['local', 'openai']:
            raise ValueError('Provider must be either "local" or "openai"')
        return v

    @validator('extract_fields')
    def validate_extract_fields(cls, v):
        if v:
            valid_fields = [
                'ProjectName', 'ClientName', 'ContractValue', 'StartDate', 'EndDate',
                'Country', 'PaymentTerms', 'ListOfServices', 'KPIs', 'SLAs', 'PenaltyClauses'
            ]
            for field in v:
                if field not in valid_fields:
                    raise ValueError(f'Invalid field: {field}')
        return v


class ContractMetadata(BaseModel):
    """Contract metadata extraction result"""
    project_name: Optional[ExtractedField] = Field(None, description="Project name")
    client_name: Optional[ExtractedField] = Field(None, description="Client name")
    contract_value: Optional[ExtractedField] = Field(None, description="Contract value")
    start_date: Optional[ExtractedField] = Field(None, description="Contract start date")
    end_date: Optional[ExtractedField] = Field(None, description="Contract end date")
    country: Optional[ExtractedField] = Field(None, description="Country")
    payment_terms: Optional[ExtractedField] = Field(None, description="Payment terms")
    list_of_services: Optional[List[ExtractedField]] = Field(None, description="List of services")
    kpis: Optional[List[ExtractedField]] = Field(None, description="Key Performance Indicators")
    slas: Optional[List[ExtractedField]] = Field(None, description="Service Level Agreements")
    penalty_clauses: Optional[List[ExtractedField]] = Field(None, description="Penalty clauses")


class MetadataResult(BaseModel):
    """Metadata extraction result"""
    metadata: ContractMetadata = Field(..., description="Extracted contract metadata")
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall extraction confidence")
    extracted_fields_count: int = Field(..., ge=0, description="Number of successfully extracted fields")
    total_fields_attempted: int = Field(..., ge=0, description="Total number of fields attempted")
    document_info: Optional[DocumentInfo] = Field(None, description="Document information")
    processing_metadata: ProcessingMetadata = Field(..., description="Processing metadata")


class MetadataResponse(BaseResponse):
    """Metadata extraction response"""
    data: Optional[MetadataResult] = Field(None, description="Metadata extraction result")
    validation: Optional[ValidationResult] = Field(None, description="Input validation result")


class ObligationRequest(BaseModel):
    """Obligation extraction request"""
    text: Optional[str] = Field(None, description="Text to extract obligations from")
    file_path: Optional[str] = Field(None, description="Path to file in storage")
    provider: Optional[str] = Field(None, description="Extraction provider (local/openai)")
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")
    include_penalties: bool = Field(True, description="Include penalty information")
    options: Optional[Dict[str, Any]] = Field(None, description="Provider-specific options")

    @validator('provider')
    def validate_provider(cls, v):
        if v and v not in ['local', 'openai']:
            raise ValueError('Provider must be either "local" or "openai"')
        return v


class Obligation(BaseModel):
    """Single obligation"""
    description: ExtractedField = Field(..., description="Obligation description")
    frequency: Optional[ExtractedField] = Field(None, description="Frequency (daily, weekly, monthly, etc.)")
    due_date: Optional[ExtractedField] = Field(None, description="Due date or deadline")
    penalty_text: Optional[ExtractedField] = Field(None, description="Penalty clause text")
    category: Optional[str] = Field(None, description="Obligation category")
    priority: Optional[str] = Field(None, description="Priority level")
    assignee: Optional[ExtractedField] = Field(None, description="Responsible party")
    status: Optional[str] = Field("pending", description="Obligation status")


class ObligationResult(BaseModel):
    """Obligation extraction result"""
    obligations: List[Obligation] = Field(..., description="Extracted obligations")
    total_obligations: int = Field(..., ge=0, description="Total number of obligations found")
    high_confidence_count: int = Field(..., ge=0, description="Number of high-confidence obligations")
    average_confidence: float = Field(..., ge=0.0, le=1.0, description="Average confidence score")
    categories: Optional[List[str]] = Field(None, description="Identified obligation categories")
    document_info: Optional[DocumentInfo] = Field(None, description="Document information")
    processing_metadata: ProcessingMetadata = Field(..., description="Processing metadata")


class ObligationResponse(BaseResponse):
    """Obligation extraction response"""
    data: Optional[ObligationResult] = Field(None, description="Obligation extraction result")
    validation: Optional[ValidationResult] = Field(None, description="Input validation result")


class BatchExtractionRequest(BaseModel):
    """Batch extraction request for multiple documents"""
    file_paths: List[str] = Field(..., min_items=1, description="List of file paths")
    extraction_type: str = Field(..., description="Type of extraction (metadata/obligations)")
    provider: Optional[str] = Field(None, description="Extraction provider")
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")
    parallel_processing: bool = Field(True, description="Process files in parallel")
    options: Optional[Dict[str, Any]] = Field(None, description="Provider-specific options")

    @validator('extraction_type')
    def validate_extraction_type(cls, v):
        if v not in ['metadata', 'obligations']:
            raise ValueError('Extraction type must be either "metadata" or "obligations"')
        return v


class BatchExtractionResult(BaseModel):
    """Batch extraction result"""
    results: List[Union[MetadataResult, ObligationResult]] = Field(..., description="Individual extraction results")
    total_files: int = Field(..., ge=1, description="Total number of files processed")
    successful_files: int = Field(..., ge=0, description="Number of successful extractions")
    failed_files: List[str] = Field(default_factory=list, description="List of failed file paths")
    total_processing_time: float = Field(..., ge=0, description="Total processing time")
    average_confidence: float = Field(..., ge=0.0, le=1.0, description="Average confidence across all results")


class BatchExtractionResponse(BaseResponse):
    """Batch extraction response"""
    data: Optional[BatchExtractionResult] = Field(None, description="Batch extraction result")


class ExtractionCapabilities(BaseModel):
    """Extraction provider capabilities"""
    provider: str = Field(..., description="Provider name")
    supported_extraction_types: List[str] = Field(..., description="Supported extraction types")
    supported_fields: Dict[str, List[str]] = Field(..., description="Supported fields by type")
    max_text_length: int = Field(..., description="Maximum text length")
    supported_languages: List[str] = Field(..., description="Supported languages")
    features: Dict[str, bool] = Field(..., description="Feature support")


class ExtractionTemplate(BaseModel):
    """Extraction template for custom field definitions"""
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    fields: Dict[str, Dict[str, Any]] = Field(..., description="Field definitions")
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="Validation rules")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)