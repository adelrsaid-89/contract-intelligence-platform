"""
Unified storage client for MinIO and local filesystem
"""

import os
import logging
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, BinaryIO
from datetime import datetime
import aiofiles
from functools import lru_cache

from minio import Minio
from minio.error import S3Error

from .config import get_settings

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Base storage exception"""
    pass


class StorageClient:
    """Unified storage client supporting both MinIO and local filesystem"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.storage_type = config.get("type", "local")
        self._client = None
        self._initialized = False

    async def initialize(self):
        """Initialize the storage client"""
        if self._initialized:
            return

        try:
            if self.storage_type == "minio":
                await self._initialize_minio()
            else:
                await self._initialize_local()

            self._initialized = True
            logger.info(f"Storage client initialized with type: {self.storage_type}")

        except Exception as e:
            logger.error(f"Failed to initialize storage client: {e}")
            raise StorageError(f"Storage initialization failed: {e}")

    async def _initialize_minio(self):
        """Initialize MinIO client"""
        try:
            endpoint = self.config["endpoint"]
            access_key = self.config["access_key"]
            secret_key = self.config["secret_key"]
            secure = endpoint.startswith("https://")

            # Remove protocol from endpoint
            if endpoint.startswith(("http://", "https://")):
                endpoint = endpoint.split("://")[1]

            self._client = Minio(
                endpoint=endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=secure
            )

            # Check if bucket exists, create if not
            bucket_name = self.config["bucket_name"]
            if not self._client.bucket_exists(bucket_name):
                self._client.make_bucket(bucket_name)
                logger.info(f"Created MinIO bucket: {bucket_name}")

        except Exception as e:
            logger.error(f"MinIO initialization failed: {e}")
            raise

    async def _initialize_local(self):
        """Initialize local filesystem storage"""
        storage_path = Path(self.config["path"])
        storage_path.mkdir(parents=True, exist_ok=True)
        self._client = storage_path
        logger.info(f"Local storage initialized at: {storage_path}")

    async def upload_file(
        self,
        file_path: str,
        content: Union[bytes, BinaryIO],
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Upload file to storage"""
        await self._ensure_initialized()

        try:
            if self.storage_type == "minio":
                return await self._upload_to_minio(file_path, content, metadata)
            else:
                return await self._upload_to_local(file_path, content, metadata)

        except Exception as e:
            logger.error(f"File upload failed for {file_path}: {e}")
            raise StorageError(f"Upload failed: {e}")

    async def _upload_to_minio(
        self,
        file_path: str,
        content: Union[bytes, BinaryIO],
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Upload to MinIO"""
        bucket_name = self.config["bucket_name"]

        if isinstance(content, bytes):
            import io
            content = io.BytesIO(content)

        # Add upload timestamp to metadata
        if metadata is None:
            metadata = {}
        metadata["upload_timestamp"] = datetime.utcnow().isoformat()

        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._client.put_object(
                    bucket_name=bucket_name,
                    object_name=file_path,
                    data=content,
                    length=-1,
                    part_size=10*1024*1024,  # 10MB parts
                    metadata=metadata
                )
            )

            return f"minio://{bucket_name}/{file_path}"

        except S3Error as e:
            logger.error(f"MinIO upload error: {e}")
            raise StorageError(f"MinIO upload failed: {e}")

    async def _upload_to_local(
        self,
        file_path: str,
        content: Union[bytes, BinaryIO],
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Upload to local filesystem"""
        full_path = self._client / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if isinstance(content, bytes):
                async with aiofiles.open(full_path, "wb") as f:
                    await f.write(content)
            else:
                async with aiofiles.open(full_path, "wb") as f:
                    if hasattr(content, 'read'):
                        data = content.read()
                        if asyncio.iscoroutine(data):
                            data = await data
                        await f.write(data)
                    else:
                        await f.write(content)

            # Store metadata in companion file
            if metadata:
                metadata_path = full_path.with_suffix(full_path.suffix + ".meta")
                import json
                metadata["upload_timestamp"] = datetime.utcnow().isoformat()
                async with aiofiles.open(metadata_path, "w") as f:
                    await f.write(json.dumps(metadata, indent=2))

            return f"file://{full_path.absolute()}"

        except Exception as e:
            logger.error(f"Local upload error: {e}")
            raise StorageError(f"Local upload failed: {e}")

    async def download_file(self, file_path: str) -> bytes:
        """Download file from storage"""
        await self._ensure_initialized()

        try:
            if self.storage_type == "minio":
                return await self._download_from_minio(file_path)
            else:
                return await self._download_from_local(file_path)

        except Exception as e:
            logger.error(f"File download failed for {file_path}: {e}")
            raise StorageError(f"Download failed: {e}")

    async def _download_from_minio(self, file_path: str) -> bytes:
        """Download from MinIO"""
        bucket_name = self.config["bucket_name"]

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self._client.get_object(bucket_name, file_path)
            )
            return response.read()

        except S3Error as e:
            logger.error(f"MinIO download error: {e}")
            raise StorageError(f"MinIO download failed: {e}")

    async def _download_from_local(self, file_path: str) -> bytes:
        """Download from local filesystem"""
        full_path = self._client / file_path

        if not full_path.exists():
            raise StorageError(f"File not found: {file_path}")

        try:
            async with aiofiles.open(full_path, "rb") as f:
                return await f.read()

        except Exception as e:
            logger.error(f"Local download error: {e}")
            raise StorageError(f"Local download failed: {e}")

    async def file_exists(self, file_path: str) -> bool:
        """Check if file exists in storage"""
        await self._ensure_initialized()

        try:
            if self.storage_type == "minio":
                return await self._file_exists_minio(file_path)
            else:
                return await self._file_exists_local(file_path)

        except Exception as e:
            logger.error(f"File existence check failed for {file_path}: {e}")
            return False

    async def _file_exists_minio(self, file_path: str) -> bool:
        """Check file existence in MinIO"""
        bucket_name = self.config["bucket_name"]

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._client.stat_object(bucket_name, file_path)
            )
            return True
        except S3Error:
            return False

    async def _file_exists_local(self, file_path: str) -> bool:
        """Check file existence in local filesystem"""
        full_path = self._client / file_path
        return full_path.exists()

    async def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        await self._ensure_initialized()

        try:
            if self.storage_type == "minio":
                return await self._delete_from_minio(file_path)
            else:
                return await self._delete_from_local(file_path)

        except Exception as e:
            logger.error(f"File deletion failed for {file_path}: {e}")
            raise StorageError(f"Delete failed: {e}")

    async def _delete_from_minio(self, file_path: str) -> bool:
        """Delete from MinIO"""
        bucket_name = self.config["bucket_name"]

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._client.remove_object(bucket_name, file_path)
            )
            return True

        except S3Error as e:
            logger.error(f"MinIO delete error: {e}")
            return False

    async def _delete_from_local(self, file_path: str) -> bool:
        """Delete from local filesystem"""
        full_path = self._client / file_path

        try:
            if full_path.exists():
                full_path.unlink()

            # Also delete metadata file if exists
            metadata_path = full_path.with_suffix(full_path.suffix + ".meta")
            if metadata_path.exists():
                metadata_path.unlink()

            return True

        except Exception as e:
            logger.error(f"Local delete error: {e}")
            return False

    async def list_files(self, prefix: str = "") -> List[Dict[str, Any]]:
        """List files in storage"""
        await self._ensure_initialized()

        try:
            if self.storage_type == "minio":
                return await self._list_files_minio(prefix)
            else:
                return await self._list_files_local(prefix)

        except Exception as e:
            logger.error(f"File listing failed: {e}")
            raise StorageError(f"List failed: {e}")

    async def _list_files_minio(self, prefix: str = "") -> List[Dict[str, Any]]:
        """List files in MinIO"""
        bucket_name = self.config["bucket_name"]
        files = []

        try:
            loop = asyncio.get_event_loop()
            objects = await loop.run_in_executor(
                None,
                lambda: list(self._client.list_objects(bucket_name, prefix=prefix))
            )

            for obj in objects:
                files.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "etag": obj.etag
                })

            return files

        except S3Error as e:
            logger.error(f"MinIO list error: {e}")
            raise StorageError(f"MinIO list failed: {e}")

    async def _list_files_local(self, prefix: str = "") -> List[Dict[str, Any]]:
        """List files in local filesystem"""
        base_path = self._client
        if prefix:
            search_path = base_path / prefix
        else:
            search_path = base_path

        files = []

        try:
            if search_path.is_dir():
                for file_path in search_path.rglob("*"):
                    if file_path.is_file() and not file_path.name.endswith(".meta"):
                        stat = file_path.stat()
                        relative_path = file_path.relative_to(base_path)

                        files.append({
                            "name": str(relative_path),
                            "size": stat.st_size,
                            "last_modified": datetime.fromtimestamp(stat.st_mtime),
                            "etag": None
                        })

            return files

        except Exception as e:
            logger.error(f"Local list error: {e}")
            raise StorageError(f"Local list failed: {e}")

    async def get_file_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file metadata"""
        await self._ensure_initialized()

        try:
            if self.storage_type == "minio":
                return await self._get_metadata_minio(file_path)
            else:
                return await self._get_metadata_local(file_path)

        except Exception as e:
            logger.error(f"Metadata retrieval failed for {file_path}: {e}")
            return None

    async def _get_metadata_minio(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get metadata from MinIO"""
        bucket_name = self.config["bucket_name"]

        try:
            loop = asyncio.get_event_loop()
            stat = await loop.run_in_executor(
                None,
                lambda: self._client.stat_object(bucket_name, file_path)
            )

            return {
                "size": stat.size,
                "last_modified": stat.last_modified,
                "etag": stat.etag,
                "content_type": stat.content_type,
                "metadata": stat.metadata
            }

        except S3Error:
            return None

    async def _get_metadata_local(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get metadata from local filesystem"""
        full_path = self._client / file_path

        if not full_path.exists():
            return None

        try:
            stat = full_path.stat()
            metadata_path = full_path.with_suffix(full_path.suffix + ".meta")

            custom_metadata = {}
            if metadata_path.exists():
                import json
                async with aiofiles.open(metadata_path, "r") as f:
                    content = await f.read()
                    custom_metadata = json.loads(content)

            return {
                "size": stat.st_size,
                "last_modified": datetime.fromtimestamp(stat.st_mtime),
                "etag": None,
                "content_type": None,
                "metadata": custom_metadata
            }

        except Exception:
            return None

    async def _ensure_initialized(self):
        """Ensure storage client is initialized"""
        if not self._initialized:
            await self.initialize()


@lru_cache()
def get_storage_client() -> StorageClient:
    """Get cached storage client instance"""
    settings = get_settings()
    config = settings.get_storage_config()
    return StorageClient(config)


async def upload_temp_file(file_content: bytes, filename: str) -> str:
    """Upload a temporary file and return the storage path"""
    storage_client = get_storage_client()

    # Generate unique filename with timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"temp/{timestamp}_{filename}"

    storage_path = await storage_client.upload_file(
        unique_filename,
        file_content,
        metadata={"type": "temporary", "original_name": filename}
    )

    return unique_filename


async def cleanup_temp_files(max_age_hours: int = 24):
    """Cleanup temporary files older than specified hours"""
    storage_client = get_storage_client()

    try:
        files = await storage_client.list_files("temp/")
        current_time = datetime.utcnow()

        for file_info in files:
            file_age = current_time - file_info["last_modified"]
            if file_age.total_seconds() > max_age_hours * 3600:
                await storage_client.delete_file(file_info["name"])
                logger.info(f"Cleaned up temporary file: {file_info['name']}")

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")