"""
Abstract base for object storage.

All storage implementations must satisfy this interface so that the
audio service remains independent of any specific storage backend.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class StoredObject:
    """Metadata returned after a successful upload."""
    object_key: str
    provider: str
    size_bytes: int
    content_type: str
    checksum: str          # SHA-256 hex digest


@dataclass
class ObjectMetadata:
    """Metadata for an existing stored object."""
    object_key: str
    size_bytes: int
    content_type: str
    exists: bool


class BaseObjectStorage(ABC):
    """Abstract object storage interface."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Short identifier for this provider, e.g. 'local' or 'minio'."""
        ...

    @abstractmethod
    def upload(
        self,
        object_key: str,
        data: bytes,
        content_type: str,
    ) -> StoredObject:
        """
        Upload binary data under the given object key.

        Args:
            object_key: Unique, safe object path/name.
            data:        Raw bytes to store.
            content_type: MIME type.

        Returns:
            StoredObject with metadata.

        Raises:
            RuntimeError: On storage backend failure.
        """
        ...

    @abstractmethod
    def exists(self, object_key: str) -> bool:
        """Return True if the object key exists in storage."""
        ...

    @abstractmethod
    def delete(self, object_key: str) -> None:
        """Delete an object. No-op if the key does not exist."""
        ...

    @abstractmethod
    def get_metadata(self, object_key: str) -> ObjectMetadata:
        """Return metadata for an existing object."""
        ...
