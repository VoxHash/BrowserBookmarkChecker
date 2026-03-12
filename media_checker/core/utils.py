"""Utility functions for media file processing."""

import hashlib
from pathlib import Path


def format_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1

    return f"{size:.2f} {units[unit_index]}"


def format_duration(seconds: float | None) -> str:
    """
    Format duration in human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "1:23:45" or "45s")
    """
    if seconds is None:
        return "N/A"

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    elif minutes > 0:
        return f"{minutes}:{secs:02d}"
    else:
        return f"{secs}s"


def calculate_file_hash(file_path: Path, algorithm: str = "md5", chunk_size: int = 8192) -> str:
    """
    Calculate hash of a file.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm ("md5" or "sha256")
        chunk_size: Chunk size for reading file

    Returns:
        Hexadecimal hash string
    """
    hash_obj = hashlib.md5() if algorithm == "md5" else hashlib.sha256()

    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except (OSError, IOError):
        return ""


def get_media_extensions() -> dict[str, list[str]]:
    """
    Get supported media file extensions.

    Returns:
        Dictionary with "video" and "audio" keys mapping to extension lists
    """
    return {
        "video": [
            ".mp4",
            ".avi",
            ".mkv",
            ".mov",
            ".wmv",
            ".flv",
            ".webm",
            ".m4v",
            ".mpg",
            ".mpeg",
            ".3gp",
            ".ogv",
            ".ts",
            ".m2ts",
            ".divx",
            ".xvid",
        ],
        "audio": [
            ".mp3",
            ".wav",
            ".flac",
            ".aac",
            ".ogg",
            ".wma",
            ".m4a",
            ".opus",
            ".ape",
            ".ac3",
            ".dts",
            ".amr",
            ".3ga",
        ],
    }


def is_media_file(file_path: Path) -> tuple[bool, str]:
    """
    Check if a file is a supported media file.

    Args:
        file_path: Path to file

    Returns:
        Tuple of (is_media, file_type) where file_type is "video", "audio", or ""
    """
    ext = file_path.suffix.lower()
    extensions = get_media_extensions()

    if ext in extensions["video"]:
        return True, "video"
    elif ext in extensions["audio"]:
        return True, "audio"
    else:
        return False, ""

