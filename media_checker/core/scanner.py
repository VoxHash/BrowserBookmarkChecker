"""Scanner for finding media files in directories."""

from pathlib import Path
from typing import Callable

from media_checker.core.models import MediaCollection, MediaFile
from media_checker.core.utils import is_media_file


def scan_directory(
    directory: str | Path,
    progress_callback: Callable[[int, int], None] | None = None,
) -> MediaCollection:
    """
    Recursively scan directory for video and audio files.

    Args:
        directory: Root directory to scan
        progress_callback: Optional callback(processed, total) for progress updates

    Returns:
        MediaCollection with found files
    """
    collection = MediaCollection()
    directory_path = Path(directory)

    if not directory_path.exists() or not directory_path.is_dir():
        return collection

    # First pass: collect all media files
    all_media_files: list[Path] = []
    for file_path in directory_path.rglob("*"):
        if file_path.is_file():
            is_media, file_type = is_media_file(file_path)
            if is_media:
                all_media_files.append(file_path)

    total = len(all_media_files)
    processed = 0

    # Second pass: create MediaFile objects
    for file_path in all_media_files:
        try:
            is_media, file_type = is_media_file(file_path)
            if not is_media:
                continue

            # Get basic file info
            stat = file_path.stat()
            file_size = stat.st_size

            # Create MediaFile with basic info (metadata will be extracted later)
            media_file = MediaFile(
                path=file_path,
                file_type=file_type,
                file_size=file_size,
            )

            collection.add(media_file)
            processed += 1

            if progress_callback:
                progress_callback(processed, total)

        except (OSError, PermissionError):
            # Skip files that can't be accessed
            processed += 1
            if progress_callback:
                progress_callback(processed, total)
            continue

    return collection

