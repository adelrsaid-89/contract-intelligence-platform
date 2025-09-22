"""
FastAPI AI Operations Microservice

This microservice provides AI-powered operations including:
- OCR (Optical Character Recognition)
- Metadata extraction from contracts
- Obligation extraction
- Q&A RAG system
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routers import ocr, metadata, obligations, qa
from utils.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("ai_service.log")
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting AI Operations Microservice")

    # Initialize services on startup
    try:
        # Test database connection if configured
        settings = get_settings()
        if settings.database_url:
            logger.info("Database connection configured")

        # Initialize FAISS index
        from rag.faiss_indexer import initialize_faiss_index
        await initialize_faiss_index()

        logger.info("AI Operations Microservice started successfully")
        yield

    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        raise
    finally:
        logger.info("Shutting down AI Operations Microservice")

# Create FastAPI application
app = FastAPI(
    title="AI Operations Microservice",
    description="FastAPI microservice for AI-powered document operations",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ocr.router, prefix="/ocr", tags=["OCR"])
app.include_router(metadata.router, prefix="/nlp", tags=["NLP"])
app.include_router(obligations.router, prefix="/nlp", tags=["NLP"])
app.include_router(qa.router, prefix="/qa", tags=["Q&A"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Operations Microservice",
        "version": "1.0.0"
    }

@app.get("/providers")
async def get_providers():
    """Get active AI providers configuration"""
    settings = get_settings()

    return {
        "ocr_provider": settings.ai_ocr_provider,
        "extract_provider": settings.ai_extract_provider,
        "available_providers": {
            "ocr": ["local", "azure"],
            "extraction": ["local", "openai"]
        },
        "features": {
            "azure_document_intelligence": bool(settings.azure_docintel_key),
            "openai_extraction": bool(settings.openai_api_key),
            "azure_openai": bool(settings.azure_openai_api_key),
            "minio_storage": bool(settings.minio_endpoint),
            "database": bool(settings.database_url)
        }
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    logger.error(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG") else "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )