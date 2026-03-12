"""Data models for media files."""

from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class MediaFile:
    """Represents a single video or audio file."""

    path: Path
    file_type: str  # "video" or "audio"
    file_size: int  # Size in bytes
    duration: float | None = None  # Duration in seconds
    width: int | None = None  # Video width in pixels
    height: int | None = None  # Video height in pixels
    codec: str | None = None  # Video/audio codec
    bitrate: int | None = None  # Bitrate in bps
    sample_rate: int | None = None  # Audio sample rate in Hz
    channels: int | None = None  # Audio channels
    file_hash: str = ""  # MD5 or SHA256 hash
    thumbnail_hash: str = ""  # Perceptual hash of thumbnail/frame
    modified_time: datetime | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        """Hash based on path."""
        return hash(str(self.path))

    def __eq__(self, other: object) -> bool:
        """Equality based on path."""
        if not isinstance(other, MediaFile):
            return False
        return self.path == other.path

    @property
    def extension(self) -> str:
        """Get file extension (lowercase)."""
        return self.path.suffix.lower()

    @property
    def name(self) -> str:
        """Get file name."""
        return self.path.name

    @property
    def parent_dir(self) -> str:
        """Get parent directory path."""
        return str(self.path.parent)


class MediaCollection:
    """Collection of media files with metadata."""

    def __init__(self) -> None:
        """Initialize an empty collection."""
        self.files: list[MediaFile] = []
        self.scan_paths: list[str] = []

    def add(self, media_file: MediaFile) -> None:
        """Add a media file to the collection."""
        self.files.append(media_file)
        parent = str(media_file.path.parent)
        if parent not in self.scan_paths:
            self.scan_paths.append(parent)

    def extend(self, media_files: list[MediaFile]) -> None:
        """Add multiple media files."""
        for media_file in media_files:
            self.add(media_file)

    def __len__(self) -> int:
        """Return the number of media files."""
        return len(self.files)

    def __iter__(self) -> Iterator[MediaFile]:
        """Iterate over media files."""
        return iter(self.files)

