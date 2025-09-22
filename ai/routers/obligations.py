"""
Obligation extraction API router
"""

import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from models.extraction_models import (
    ObligationRequest, ObligationResponse, BatchExtractionRequest, BatchExtractionResponse,
    ExtractionCapabilities, ValidationResult
)
from models.common_models import ErrorResponse
from services.extract_local import LocalExtractionService
from services.extract_openai import OpenAIExtractionService
from utils.config import get_settings
from utils.storage_client import get_storage_client

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_extraction_service():
    """Get extraction service based on configuration"""
    settings = get_settings()

    if settings.ai_extract_provider == "openai":
        if not settings.openai_api_key and not (settings.azure_openai_api_key and settings.azure_openai_endpoint):
            raise HTTPException(
                status_code=500,
                detail="OpenAI/Azure OpenAI not configured"
            )
        return OpenAIExtractionService()
    else:
        return LocalExtractionService()


@router.post("/obligations", response_model=ObligationResponse)
async def extract_obligations(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = None,
    provider: Optional[str] = None,
    confidence_threshold: float = 0.5,
    include_penalties: bool = True
):
    """
    Extract contractual obligations from document or text

    - **file**: Document file (PDF, TXT, etc.) - optional if text is provided
    - **text**: Raw text content - optional if file is provided
    - **provider**: Extraction provider (local/openai) - optional, uses default if not specified
    - **confidence_threshold**: Minimum confidence threshold (0.0-1.0)
    - **include_penalties**: Whether to include penalty information
    """
    try:
        # Validate input
        if not file and not text:
            raise HTTPException(
                status_code=400,
                detail="Either file or text must be provided"
            )

        # Get text content
        if file:
            file_content = await file.read()
            # For simplicity, assume text files or use OCR result
            if file.filename.endswith('.txt'):
                text_content = file_content.decode('utf-8')
            else:
                # In a real implementation, you'd use OCR first
                raise HTTPException(
                    status_code=400,
                    detail="For non-text files, use OCR endpoint first to extract text"
                )
        else:
            text_content = text

        # Create request
        request = ObligationRequest(
            text=text_content,
            provider=provider,
            confidence_threshold=confidence_threshold,
            include_penalties=include_penalties
        )

        # Validate request
        validation = await validate_obligation_request(request)
        if not validation.is_valid:
            return ObligationResponse(
                success=False,
                message="Invalid request",
                validation=validation
            )

        # Get extraction service
        if request.provider:
            if request.provider == "openai":
                extraction_service = OpenAIExtractionService()
            else:
                extraction_service = LocalExtractionService()
        else:
            extraction_service = await get_extraction_service()

        # Extract obligations
        try:
            result = await extraction_service.extract_obligations(request, text_content)

            return ObligationResponse(
                success=True,
                message=f"Extracted {result.total_obligations} obligations successfully",
                data=result,
                validation=validation
            )

        except Exception as e:
            logger.error(f"Obligation extraction failed: {e}")
            raise HTTPException(status_code=500, detail=f"Obligation extraction failed: {str(e)}")

        finally:
            # Clean up OpenAI client if used
            if hasattr(extraction_service, 'close'):
                await extraction_service.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Obligations endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/obligations-from-storage", response_model=ObligationResponse)
async def extract_obligations_from_storage(
    request: ObligationRequest,
    background_tasks: BackgroundTasks
):
    """
    Extract obligations from document stored in the storage system

    - **file_path**: Path to file in storage system
    - **provider**: Extraction provider (local/openai)
    - **confidence_threshold**: Minimum confidence threshold
    - **include_penalties**: Whether to include penalty information
    """
    try:
        if not request.file_path:
            raise HTTPException(status_code=400, detail="file_path is required")

        # Validate request
        validation = await validate_obligation_request(request)
        if not validation.is_valid:
            return ObligationResponse(
                success=False,
                message="Invalid request",
                validation=validation
            )

        # Get file from storage
        storage_client = get_storage_client()
        await storage_client.initialize()

        if not await storage_client.file_exists(request.file_path):
            raise HTTPException(status_code=404, detail="File not found in storage")

        file_content = await storage_client.download_file(request.file_path)

        # For simplicity, assume text files or that OCR was already done
        try:
            text_content = file_content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="File is not a text file. Use OCR endpoint first to extract text."
            )

        # Get extraction service
        if request.provider:
            if request.provider == "openai":
                extraction_service = OpenAIExtractionService()
            else:
                extraction_service = LocalExtractionService()
        else:
            extraction_service = await get_extraction_service()

        # Extract obligations
        try:
            result = await extraction_service.extract_obligations(request, text_content)

            return ObligationResponse(
                success=True,
                message=f"Extracted {result.total_obligations} obligations successfully",
                data=result,
                validation=validation
            )

        except Exception as e:
            logger.error(f"Obligation extraction failed: {e}")
            raise HTTPException(status_code=500, detail=f"Obligation extraction failed: {str(e)}")

        finally:
            # Clean up OpenAI client if used
            if hasattr(extraction_service, 'close'):
                await extraction_service.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Obligations storage endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/batch-obligations", response_model=BatchExtractionResponse)
async def batch_extract_obligations(
    request: BatchExtractionRequest,
    background_tasks: BackgroundTasks
):
    """
    Extract obligations from multiple documents in batch

    - **file_paths**: List of file paths in storage
    - **extraction_type**: Type of extraction (must be 'obligations')
    - **provider**: Extraction provider (local/openai)
    - **confidence_threshold**: Minimum confidence threshold
    - **parallel_processing**: Process files in parallel
    """
    try:
        # Validate request
        if request.extraction_type != "obligations":
            raise HTTPException(
                status_code=400,
                detail="extraction_type must be 'obligations' for this endpoint"
            )

        if not request.file_paths:
            raise HTTPException(status_code=400, detail="file_paths cannot be empty")

        if len(request.file_paths) > 50:
            raise HTTPException(status_code=400, detail="Maximum 50 files per batch")

        # Get storage client
        storage_client = get_storage_client()
        await storage_client.initialize()

        # Get extraction service
        if request.provider:
            if request.provider == "openai":
                extraction_service = OpenAIExtractionService()
            else:
                extraction_service = LocalExtractionService()
        else:
            extraction_service = await get_extraction_service()

        # Process files
        import asyncio
        import time

        start_time = time.time()
        results = []
        failed_files = []

        try:
            if request.parallel_processing:
                # Process in parallel
                tasks = []
                for file_path in request.file_paths:
                    task = process_single_obligation_file(
                        extraction_service, storage_client, file_path, request
                    )
                    tasks.append(task)

                completed_results = await asyncio.gather(*tasks, return_exceptions=True)

                for i, result in enumerate(completed_results):
                    if isinstance(result, Exception):
                        failed_files.append(request.file_paths[i])
                        logger.error(f"Failed to process {request.file_paths[i]}: {result}")
                    else:
                        results.append(result)

            else:
                # Process sequentially
                for file_path in request.file_paths:
                    try:
                        result = await process_single_obligation_file(
                            extraction_service, storage_client, file_path, request
                        )
                        results.append(result)
                    except Exception as e:
                        failed_files.append(file_path)
                        logger.error(f"Failed to process {file_path}: {e}")

            total_processing_time = time.time() - start_time

            # Calculate average confidence
            all_confidences = [r.average_confidence for r in results]
            average_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0

            from models.extraction_models import BatchExtractionResult
            batch_result = BatchExtractionResult(
                results=results,
                total_files=len(request.file_paths),
                successful_files=len(results),
                failed_files=failed_files,
                total_processing_time=total_processing_time,
                average_confidence=average_confidence
            )

            return BatchExtractionResponse(
                success=True,
                message=f"Processed {len(results)}/{len(request.file_paths)} files successfully",
                data=batch_result
            )

        finally:
            # Clean up OpenAI client if used
            if hasattr(extraction_service, 'close'):
                await extraction_service.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch obligations endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def process_single_obligation_file(
    extraction_service, storage_client, file_path: str, batch_request: BatchExtractionRequest
):
    """Process a single file for batch obligation extraction"""
    try:
        # Check if file exists
        if not await storage_client.file_exists(file_path):
            raise Exception(f"File not found: {file_path}")

        # Download file
        file_content = await storage_client.download_file(file_path)

        # Decode text content
        try:
            text_content = file_content.decode('utf-8')
        except UnicodeDecodeError:
            raise Exception(f"File is not a text file: {file_path}")

        # Create individual request
        individual_request = ObligationRequest(
            text=text_content,
            file_path=file_path,
            provider=batch_request.provider,
            confidence_threshold=batch_request.confidence_threshold,
            include_penalties=batch_request.options.get('include_penalties', True) if batch_request.options else True,
            options=batch_request.options
        )

        # Extract obligations
        result = await extraction_service.extract_obligations(individual_request, text_content)
        return result

    except Exception as e:
        logger.error(f"Single obligation file processing failed for {file_path}: {e}")
        raise


@router.get("/capabilities", response_model=ExtractionCapabilities)
async def get_obligation_capabilities():
    """Get obligation extraction service capabilities"""
    try:
        extraction_service = await get_extraction_service()
        capabilities = await extraction_service.get_capabilities()
        return ExtractionCapabilities(**capabilities)

    except Exception as e:
        logger.error(f"Capabilities endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get capabilities")


@router.get("/obligation-categories")
async def get_obligation_categories():
    """Get available obligation categories"""
    try:
        categories = [
            {
                "name": "reporting",
                "description": "Reporting and documentation obligations",
                "examples": ["Submit monthly reports", "Provide status updates"]
            },
            {
                "name": "maintenance",
                "description": "Maintenance and service obligations",
                "examples": ["Maintain equipment", "Perform regular inspections"]
            },
            {
                "name": "delivery",
                "description": "Delivery and provision obligations",
                "examples": ["Deliver goods", "Provide services"]
            },
            {
                "name": "compliance",
                "description": "Compliance and regulatory obligations",
                "examples": ["Follow safety regulations", "Adhere to standards"]
            },
            {
                "name": "payment",
                "description": "Payment and financial obligations",
                "examples": ["Make payments", "Pay invoices"]
            },
            {
                "name": "performance",
                "description": "Performance and execution obligations",
                "examples": ["Complete tasks", "Achieve targets"]
            },
            {
                "name": "general",
                "description": "General obligations not fitting other categories",
                "examples": ["Other contractual obligations"]
            }
        ]

        return {
            "success": True,
            "message": "Obligation categories retrieved successfully",
            "data": {
                "categories": categories,
                "total_categories": len(categories)
            }
        }

    except Exception as e:
        logger.error(f"Categories endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get categories")


async def validate_obligation_request(request: ObligationRequest) -> ValidationResult:
    """Validate obligation extraction request"""
    errors = []
    warnings = []

    try:
        # Validate provider
        if request.provider and request.provider not in ['local', 'openai']:
            errors.append("Provider must be 'local' or 'openai'")

        # Validate provider configuration
        settings = get_settings()

        if request.provider == "openai" or (not request.provider and settings.ai_extract_provider == "openai"):
            if not settings.openai_api_key and not (settings.azure_openai_api_key and settings.azure_openai_endpoint):
                errors.append("OpenAI/Azure OpenAI credentials not configured")

        # Validate confidence threshold
        if not (0.0 <= request.confidence_threshold <= 1.0):
            errors.append("Confidence threshold must be between 0.0 and 1.0")

        # Validate text length
        if request.text and len(request.text) > 100000:
            warnings.append("Text is very long and may affect processing time")

        # Check if text is too short for meaningful obligation extraction
        if request.text and len(request.text) < 50:
            warnings.append("Text is very short and may not contain meaningful obligations")

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