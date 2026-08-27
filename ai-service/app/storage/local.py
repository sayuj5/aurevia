"""
Local filesystem object storage implementation.

Used for development and DEMO_MODE. Stores files under
settings.LOCAL_STORAGE_PATH.

Never uses the original filename — all paths are generated from
the object_key provided by the caller.
"""

import hashlib
import os
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.logging import logger
from app.storage.base import BaseObjectStorage, ObjectMetadata, StoredObject


class LocalObjectStorage(BaseObjectStorage):
    """
    Local-disk storage backend.

    Safe path construction: the base directory is set at init time and
    every object_key is sanitised before use so user-controlled input
    cannot escape the base directory (path traversal protection).
    """

    def __init__(self, base_path: Optional[str] = None) -> None:
        raw = base_path or settings.LOCAL_STORAGE_PATH
        self._base = Path(raw).resolve()
        self._base.mkdir(parents=True, exist_ok=True)
        logger.info("LocalObjectStorage initialised at %s", self._base)

    @property
    def provider_name(self) -> str:
        return "local"

    # ------------------------------------------------------------------
    # Interface implementation
    # ------------------------------------------------------------------

    def upload(
        self,
        object_key: str,
        data: bytes,
        content_type: str,
    ) -> StoredObject:
        dest = self._safe_path(object_key)
        dest.parent.mkdir(parents=True, exist_ok=True)

        checksum = hashlib.sha256(data).hexdigest()
        dest.write_bytes(data)

        logger.debug(
            "LocalStorage.upload: key=%s bytes=%d", object_key, len(data)
        )
        return StoredObject(
            object_key=object_key,
            provider=self.provider_name,
            size_bytes=len(data),
            content_type=content_type,
            checksum=checksum,
        )

    def exists(self, object_key: str) -> bool:
        return self._safe_path(object_key).is_file()

    def delete(self, object_key: str) -> None:
        path = self._safe_path(object_key)
        if path.is_file():
            path.unlink()
            logger.debug("LocalStorage.delete: key=%s", object_key)

    def get_metadata(self, object_key: str) -> ObjectMetadata:
        path = self._safe_path(object_key)
        if not path.is_file():
            return ObjectMetadata(
                object_key=object_key,
                size_bytes=0,
                content_type="",
                exists=False,
            )
        stat = path.stat()
        return ObjectMetadata(
            object_key=object_key,
            size_bytes=stat.st_size,
            content_type="application/octet-stream",
            exists=True,
        )

    # ------------------------------------------------------------------
    # Path-traversal protection
    # ------------------------------------------------------------------

    def _safe_path(self, object_key: str) -> Path:
        """
        Resolve the final filesystem path.

        Ensures the resolved path is always inside self._base.
        Raises ValueError on path-traversal attempts.
        """
        # Strip leading slashes / backslashes to prevent absolute paths
        sanitised = object_key.lstrip("/\\")
        candidate = (self._base / sanitised).resolve()

        # Guard: must remain inside the base directory
        try:
            candidate.relative_to(self._base)
        except ValueError:
            raise ValueError(
                f"Path traversal attempt detected for key: {object_key!r}"
            )
        return candidate


# Optional import guard — type hint only
from typing import Optional  # noqa: E402 (kept at bottom for clarity)
