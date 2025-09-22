"""
OCR API router
"""

import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from models.ocr_models import (
    OCRRequest, OCRResponse, OCRBatchRequest, OCRBatchResponse,
    OCRCapabilities, ValidationResult
)
from models.common_models import ErrorResponse
from services.ocr_local import LocalOCRService
from services.ocr_azure import AzureOCRService
from utils.config import get_settings
from utils.storage_client import get_storage_client, upload_temp_file

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_ocr_service():
    """Get OCR service based on configuration"""
    settings = get_settings()

    if settings.ai_ocr_provider == "azure":
        if not settings.azure_docintel_endpoint or not settings.azure_docintel_key:
            raise HTTPException(
                status_code=500,
                detail="Azure Document Intelligence not configured"
            )
        return AzureOCRService()
    else:
        return LocalOCRService()


@router.post("/extract", response_model=OCRResponse)
async def extract_text(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    provider: Optional[str] = None,
    languages: Optional[str] = None,
    extract_layout: bool = True,
    extract_tables: bool = True
):
    """
    Extract text from uploaded document using OCR

    - **file**: Document file (PDF, PNG, JPG, etc.)
    - **provider**: OCR provider (local/azure) - optional, uses default if not specified
    - **languages**: Comma-separated language codes (e.g., "eng,spa")
    - **extract_layout**: Whether to extract layout information
    - **extract_tables**: Whether to extract table structures
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Check file size
        settings = get_settings()
        file_content = await file.read()

        if len(file_content) > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.max_file_size} bytes"
            )

        # Check file type
        supported_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
        file_ext = '.' + file.filename.split('.')[-1].lower()

        if file_ext not in supported_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported: {', '.join(supported_extensions)}"
            )

        # Parse languages
        language_list = None
        if languages:
            language_list = [lang.strip() for lang in languages.split(',')]

        # Create request
        request = OCRRequest(
            provider=provider,
            languages=language_list,
            extract_layout=extract_layout,
            extract_tables=extract_tables
        )

        # Validate request
        validation = await validate_ocr_request(request)
        if not validation.is_valid:
            return OCRResponse(
                success=False,
                message="Invalid request",
                validation=validation
            )

        # Get OCR service
        if request.provider:
            if request.provider == "azure":
                ocr_service = AzureOCRService()
            else:
                ocr_service = LocalOCRService()
        else:
            ocr_service = await get_ocr_service()

        # Process document
        try:
            result = await ocr_service.extract_text(request, file_content, file.filename)

            return OCRResponse(
                success=True,
                message="Text extracted successfully",
                data=result,
                validation=validation
            )

        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

        finally:
            # Clean up Azure client if used
            if hasattr(ocr_service, 'close'):
                await ocr_service.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/extract-from-storage", response_model=OCRResponse)
async def extract_text_from_storage(
    request: OCRRequest,
    background_tasks: BackgroundTasks
):
    """
    Extract text from document stored in the storage system

    - **file_path**: Path to file in storage system
    - **provider**: OCR provider (local/azure)
    - **languages**: Language codes for OCR
    - **extract_layout**: Whether to extract layout information
    - **extract_tables**: Whether to extract table structures
    """
    try:
        if not request.file_path:
            raise HTTPException(status_code=400, detail="file_path is required")

        # Validate request
        validation = await validate_ocr_request(request)
        if not validation.is_valid:
            return OCRResponse(
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
        filename = request.file_path.split('/')[-1]

        # Get OCR service
        if request.provider:
            if request.provider == "azure":
                ocr_service = AzureOCRService()
            else:
                ocr_service = LocalOCRService()
        else:
            ocr_service = await get_ocr_service()

        # Process document
        try:
            result = await ocr_service.extract_text(request, file_content, filename)

            return OCRResponse(
                success=True,
                message="Text extracted successfully",
                data=result,
                validation=validation
            )

        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

        finally:
            # Clean up Azure client if used
            if hasattr(ocr_service, 'close'):
                await ocr_service.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR storage endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/batch-extract", response_model=OCRBatchResponse)
async def batch_extract_text(
    request: OCRBatchRequest,
    background_tasks: BackgroundTasks
):
    """
    Extract text from multiple documents in batch

    - **file_paths**: List of file paths in storage
    - **provider**: OCR provider (local/azure)
    - **languages**: Language codes for OCR
    - **extract_layout**: Whether to extract layout information
    - **extract_tables**: Whether to extract table structures
    - **parallel_processing**: Process files in parallel
    """
    try:
        # Validate request
        if not request.file_paths:
            raise HTTPException(status_code=400, detail="file_paths cannot be empty")

        if len(request.file_paths) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 files per batch")

        # Get storage client
        storage_client = get_storage_client()
        await storage_client.initialize()

        # Get OCR service
        if request.provider:
            if request.provider == "azure":
                ocr_service = AzureOCRService()
            else:
                ocr_service = LocalOCRService()
        else:
            ocr_service = await get_ocr_service()

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
                    task = process_single_file(ocr_service, storage_client, file_path, request)
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
                        result = await process_single_file(ocr_service, storage_client, file_path, request)
                        results.append(result)
                    except Exception as e:
                        failed_files.append(file_path)
                        logger.error(f"Failed to process {file_path}: {e}")

            total_processing_time = time.time() - start_time

            from models.ocr_models import OCRBatchResult
            batch_result = OCRBatchResult(
                results=results,
                total_files=len(request.file_paths),
                successful_files=len(results),
                failed_files=failed_files,
                total_processing_time=total_processing_time
            )

            return OCRBatchResponse(
                success=True,
                message=f"Processed {len(results)}/{len(request.file_paths)} files successfully",
                data=batch_result
            )

        finally:
            # Clean up Azure client if used
            if hasattr(ocr_service, 'close'):
                await ocr_service.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch OCR endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def process_single_file(ocr_service, storage_client, file_path: str, batch_request: OCRBatchRequest):
    """Process a single file for batch OCR"""
    try:
        # Check if file exists
        if not await storage_client.file_exists(file_path):
            raise Exception(f"File not found: {file_path}")

        # Download file
        file_content = await storage_client.download_file(file_path)
        filename = file_path.split('/')[-1]

        # Create individual request
        individual_request = OCRRequest(
            file_path=file_path,
            provider=batch_request.provider,
            languages=batch_request.languages,
            extract_layout=batch_request.extract_layout,
            extract_tables=batch_request.extract_tables,
            options=batch_request.options
        )

        # Process file
        result = await ocr_service.extract_text(individual_request, file_content, filename)
        return result

    except Exception as e:
        logger.error(f"Single file processing failed for {file_path}: {e}")
        raise


@router.get("/capabilities", response_model=OCRCapabilities)
async def get_capabilities():
    """Get OCR service capabilities"""
    try:
        ocr_service = await get_ocr_service()
        capabilities = await ocr_service.get_capabilities()
        return OCRCapabilities(**capabilities)

    except Exception as e:
        logger.error(f"Capabilities endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get capabilities")


async def validate_ocr_request(request: OCRRequest) -> ValidationResult:
    """Validate OCR request"""
    errors = []
    warnings = []

    try:
        # Validate provider
        if request.provider and request.provider not in ['local', 'azure']:
            errors.append("Provider must be 'local' or 'azure'")

        # Validate provider configuration
        settings = get_settings()

        if request.provider == "azure" or (not request.provider and settings.ai_ocr_provider == "azure"):
            if not settings.azure_docintel_endpoint or not settings.azure_docintel_key:
                errors.append("Azure Document Intelligence credentials not configured")

        # Validate languages
        if request.languages:
            valid_languages = ['eng', 'spa', 'fra', 'deu', 'ita', 'por', 'rus', 'chi_sim', 'jpn', 'kor']
            for lang in request.languages:
                if lang not in valid_languages:
                    warnings.append(f"Language '{lang}' may not be supported by all providers")

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