"""
Configuration management for AI Operations Microservice
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings"""

    # AI Provider Configuration
    ai_ocr_provider: str = Field(default="local", env="AI_OCR_PROVIDER")
    ai_extract_provider: str = Field(default="local", env="AI_EXTRACT_PROVIDER")

    # Azure OpenAI Configuration
    azure_openai_api_key: Optional[str] = Field(default=None, env="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: Optional[str] = Field(default=None, env="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_version: str = Field(default="2023-12-01-preview", env="AZURE_OPENAI_API_VERSION")
    azure_openai_deployment_name: str = Field(default="gpt-4", env="AZURE_OPENAI_DEPLOYMENT_NAME")

    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")

    # Azure Document Intelligence Configuration
    azure_docintel_endpoint: Optional[str] = Field(default=None, env="AZURE_DOCINTEL_ENDPOINT")
    azure_docintel_key: Optional[str] = Field(default=None, env="AZURE_DOCINTEL_KEY")

    # MinIO Configuration
    minio_endpoint: Optional[str] = Field(default=None, env="MINIO_ENDPOINT")
    minio_access_key: Optional[str] = Field(default=None, env="MINIO_ACCESS_KEY")
    minio_secret_key: Optional[str] = Field(default=None, env="MINIO_SECRET_KEY")
    minio_bucket_name: str = Field(default="documents", env="MINIO_BUCKET_NAME")

    # Database Configuration
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")

    # Local Storage Configuration
    local_storage_path: str = Field(default="./data", env="LOCAL_STORAGE_PATH")

    # FAISS Configuration
    faiss_index_path: str = Field(default="./faiss_index", env="FAISS_INDEX_PATH")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL")

    # Tesseract Configuration
    tesseract_cmd: str = Field(default="tesseract", env="TESSERACT_CMD")
    tesseract_data_path: Optional[str] = Field(default=None, env="TESSDATA_PREFIX")

    # Model Configuration
    local_extract_model: str = Field(
        default="microsoft/layoutlmv3-base",
        env="LOCAL_EXTRACT_MODEL"
    )

    # Application Configuration
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    max_file_size: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE")  # 50MB

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")

    class Config:
        env_file = ".env"
        case_sensitive = False

    def validate_ocr_provider(self) -> bool:
        """Validate OCR provider configuration"""
        if self.ai_ocr_provider == "azure":
            return bool(self.azure_docintel_endpoint and self.azure_docintel_key)
        return True  # Local provider always available

    def validate_extract_provider(self) -> bool:
        """Validate extraction provider configuration"""
        if self.ai_extract_provider == "openai":
            return bool(self.openai_api_key or
                       (self.azure_openai_api_key and self.azure_openai_endpoint))
        return True  # Local provider always available

    def get_storage_config(self) -> dict:
        """Get storage configuration"""
        if self.minio_endpoint:
            return {
                "type": "minio",
                "endpoint": self.minio_endpoint,
                "access_key": self.minio_access_key,
                "secret_key": self.minio_secret_key,
                "bucket_name": self.minio_bucket_name
            }
        else:
            return {
                "type": "local",
                "path": self.local_storage_path
            }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


def validate_configuration():
    """Validate the current configuration"""
    settings = get_settings()

    issues = []

    # Validate OCR provider
    if not settings.validate_ocr_provider():
        issues.append(f"OCR provider '{settings.ai_ocr_provider}' is not properly configured")

    # Validate extraction provider
    if not settings.validate_extract_provider():
        issues.append(f"Extraction provider '{settings.ai_extract_provider}' is not properly configured")

    # Check for required directories
    if not os.path.exists(settings.local_storage_path):
        try:
            os.makedirs(settings.local_storage_path, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create local storage directory: {e}")

    if not os.path.exists(settings.faiss_index_path):
        try:
            os.makedirs(settings.faiss_index_path, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create FAISS index directory: {e}")

    return issues


# Environment configuration templates
def create_env_example():
    """Create .env.example file with all configuration options"""
    env_example = """# AI Provider Configuration
AI_OCR_PROVIDER=local  # local, azure
AI_EXTRACT_PROVIDER=local  # local, openai

# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-12-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# OpenAI Configuration
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4

# Azure Document Intelligence Configuration
AZURE_DOCINTEL_ENDPOINT=https://your-docintel.cognitiveservices.azure.com/
AZURE_DOCINTEL_KEY=your_docintel_key

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=documents

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Local Storage Configuration
LOCAL_STORAGE_PATH=./data

# FAISS Configuration
FAISS_INDEX_PATH=./faiss_index
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Tesseract Configuration
TESSERACT_CMD=tesseract
TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

# Model Configuration
LOCAL_EXTRACT_MODEL=microsoft/layoutlmv3-base

# Application Configuration
DEBUG=false
LOG_LEVEL=INFO
MAX_FILE_SIZE=52428800  # 50MB
RATE_LIMIT_PER_MINUTE=60

# Server Configuration
HOST=0.0.0.0
PORT=8000
"""
    return env_example