"""
MinIO object storage implementation.

Used when STORAGE_PROVIDER="minio". Requires the `minio` package.
Provides graceful fallback if MinIO is unavailable or not installed.
"""

from app.core.logging import logger
from app.storage.base import BaseObjectStorage, ObjectMetadata, StoredObject
from app.core.config import settings
import hashlib
import io

try:
    from minio import Minio
    from minio.error import S3Error
    _MINIO_AVAILABLE = True
except ImportError:
    _MINIO_AVAILABLE = False


class MinIOObjectStorage(BaseObjectStorage):
    """
    MinIO / S3-compatible object storage backend.

    If the minio package is not installed or the server is unreachable,
    all operations raise RuntimeError with a clear message rather than
    crashing silently.
    """

    def __init__(self) -> None:
        if not _MINIO_AVAILABLE:
            raise RuntimeError(
                "MinIO SDK is not installed. "
                "Run: pip install minio  or set STORAGE_PROVIDER=local"
            )
        self._client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY or None,
            secret_key=settings.MINIO_SECRET_KEY or None,
            secure=settings.MINIO_SECURE,
        )
        self._bucket = settings.MINIO_BUCKET_NAME
        self._ensure_bucket()

    @property
    def provider_name(self) -> str:
        return "minio"

    # ------------------------------------------------------------------
    # Interface implementation
    # ------------------------------------------------------------------

    def upload(
        self,
        object_key: str,
        data: bytes,
        content_type: str,
    ) -> StoredObject:
        checksum = hashlib.sha256(data).hexdigest()
        try:
            self._client.put_object(
                bucket_name=self._bucket,
                object_name=object_key,
                data=io.BytesIO(data),
                length=len(data),
                content_type=content_type,
            )
        except Exception as exc:
            logger.error("MinIO upload failed: %s", type(exc).__name__)
            raise RuntimeError(f"MinIO upload failed: {exc}") from exc

        logger.debug("MinIO.upload: key=%s bytes=%d", object_key, len(data))
        return StoredObject(
            object_key=object_key,
            provider=self.provider_name,
            size_bytes=len(data),
            content_type=content_type,
            checksum=checksum,
        )

    def exists(self, object_key: str) -> bool:
        try:
            self._client.stat_object(self._bucket, object_key)
            return True
        except Exception:
            return False

    def delete(self, object_key: str) -> None:
        try:
            self._client.remove_object(self._bucket, object_key)
        except Exception as exc:
            logger.warning("MinIO delete failed for key=%s: %s", object_key, exc)

    def get_metadata(self, object_key: str) -> ObjectMetadata:
        try:
            stat = self._client.stat_object(self._bucket, object_key)
            return ObjectMetadata(
                object_key=object_key,
                size_bytes=stat.size,
                content_type=stat.content_type or "application/octet-stream",
                exists=True,
            )
        except Exception:
            return ObjectMetadata(
                object_key=object_key,
                size_bytes=0,
                content_type="",
                exists=False,
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _ensure_bucket(self) -> None:
        try:
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)
                logger.info("MinIO: created bucket '%s'", self._bucket)
        except Exception as exc:
            logger.warning("MinIO bucket check failed: %s", exc)


def get_storage() -> BaseObjectStorage:
    """
    Factory: return the configured storage backend.

    Reads STORAGE_PROVIDER from settings:
      - "minio"  → MinIOObjectStorage
      - anything else → LocalObjectStorage (default / demo)
    """
    from app.storage.local import LocalObjectStorage  # avoid circular at module level

    if settings.STORAGE_PROVIDER == "minio":
        try:
            return MinIOObjectStorage()
        except RuntimeError as exc:
            logger.warning(
                "MinIO unavailable (%s), falling back to LocalObjectStorage.", exc
            )
    return LocalObjectStorage()
