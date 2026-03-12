"""Deduplication logic for media files."""

from collections import defaultdict
from typing import Any

from media_checker.core.models import MediaFile, MediaCollection


def group_duplicates(
    collection: MediaCollection,
    match_by_hash: bool = True,
    match_by_size_duration: bool = True,
    match_by_thumbnail: bool = True,
    duration_tolerance: float = 1.0,
) -> tuple[dict[str, list[MediaFile]], list[dict[str, Any]]]:
    """
    Group duplicate media files using multiple matching strategies.

    Args:
        collection: Collection to deduplicate
        match_by_hash: Match files with identical hash (exact duplicates)
        match_by_size_duration: Match files with same size and similar duration
        match_by_thumbnail: Match videos with similar thumbnail hash (visual similarity)
        duration_tolerance: Tolerance in seconds for duration matching

    Returns:
        Tuple of (grouped dict, report list)
        - grouped: dict mapping group key to list of MediaFile objects
        - report: list of dicts with dedupe statistics
    """
    grouped: dict[str, list[MediaFile]] = defaultdict(list)
    processed: set[MediaFile] = set()

    # Strategy 1: Match by hash (exact duplicates)
    if match_by_hash:
        hash_groups: dict[str, list[MediaFile]] = defaultdict(list)
        for media_file in collection.files:
            if media_file.file_hash:
                hash_groups[media_file.file_hash].append(media_file)

        for file_hash, files in hash_groups.items():
            if len(files) > 1:
                group_key = f"hash_{file_hash[:8]}"
                grouped[group_key] = files
                processed.update(files)

    # Strategy 2: Match by size + duration (likely duplicates)
    if match_by_size_duration:
        size_duration_groups: dict[tuple[int, float | None], list[MediaFile]] = defaultdict(list)
        for media_file in collection.files:
            if media_file in processed:
                continue
            # Round duration to tolerance
            duration_key: float | None = None
            if media_file.duration is not None:
                duration_key = round(media_file.duration / duration_tolerance) * duration_tolerance

            key = (media_file.file_size, duration_key)
            size_duration_groups[key].append(media_file)

        for key, files in size_duration_groups.items():
            if len(files) > 1:
                # Further filter by duration tolerance
                filtered_files = []
                for file1 in files:
                    group = [file1]
                    for file2 in files:
                        if file1 == file2:
                            continue
                        if (
                            file1.duration is not None
                            and file2.duration is not None
                            and abs(file1.duration - file2.duration) <= duration_tolerance
                        ):
                            group.append(file2)
                    if len(group) > 1:
                        filtered_files.extend(group)

                if filtered_files:
                    # Remove duplicates from filtered_files
                    unique_files = list(dict.fromkeys(filtered_files))
                    if len(unique_files) > 1:
                        group_key = f"size_duration_{key[0]}_{key[1]}"
                        grouped[group_key] = unique_files
                        processed.update(unique_files)

    # Strategy 3: Match videos by thumbnail hash (visual similarity)
    if match_by_thumbnail:
        thumbnail_groups: dict[str, list[MediaFile]] = defaultdict(list)
        for media_file in collection.files:
            if media_file in processed:
                continue
            if media_file.file_type == "video" and media_file.thumbnail_hash:
                thumbnail_groups[media_file.thumbnail_hash].append(media_file)

        for thumbnail_hash, files in thumbnail_groups.items():
            if len(files) > 1:
                # Check if thumbnails are similar (hamming distance <= 5)
                similar_groups: list[list[MediaFile]] = []
                for file1 in files:
                    found_group = False
                    for group in similar_groups:
                        # Check if file1 is similar to any file in this group
                        for file2 in group:
                            if _thumbnail_similar(file1.thumbnail_hash, file2.thumbnail_hash):
                                group.append(file1)
                                found_group = True
                                break
                        if found_group:
                            break

                    if not found_group:
                        similar_groups.append([file1])

                for group in similar_groups:
                    if len(group) > 1:
                        group_key = f"thumbnail_{thumbnail_hash[:8]}"
                        grouped[group_key] = group
                        processed.update(group)

    # Strategy 4: Match by size + codec + duration for audio
    codec_groups: dict[tuple[int, str | None, float | None], list[MediaFile]] = defaultdict(list)
    for media_file in collection.files:
        if media_file in processed:
            continue
        if media_file.file_type == "audio":
            duration_key: float | None = None
            if media_file.duration is not None:
                duration_key = round(media_file.duration / duration_tolerance) * duration_tolerance

            key = (media_file.file_size, media_file.codec, duration_key)
            codec_groups[key].append(media_file)

    for key, files in codec_groups.items():
        if len(files) > 1:
            # Filter by duration tolerance
            filtered_files = []
            for file1 in files:
                group = [file1]
                for file2 in files:
                    if file1 == file2:
                        continue
                    if (
                        file1.duration is not None
                        and file2.duration is not None
                        and abs(file1.duration - file2.duration) <= duration_tolerance
                    ):
                        group.append(file2)
                if len(group) > 1:
                    filtered_files.extend(group)

            if filtered_files:
                unique_files = list(dict.fromkeys(filtered_files))
                if len(unique_files) > 1:
                    group_key = f"codec_{key[0]}_{key[1]}_{key[2]}"
                    if group_key not in grouped:
                        grouped[group_key] = unique_files
                        processed.update(unique_files)

    # Generate report
    report: list[dict[str, Any]] = []

    for group_key, files in grouped.items():
        if not files:
            continue

        # Get unique paths
        paths = sorted(set(str(f.path) for f in files))
        parent_dirs = sorted(set(f.parent_dir for f in files))

        # Representative file (first one)
        representative = files[0]

        report.append(
            {
                "group_key": group_key,
                "file_type": representative.file_type,
                "count": len(files),
                "file_size": representative.file_size,
                "duration": representative.duration,
                "paths": paths,
                "parent_dirs": parent_dirs,
                "codec": representative.codec,
                "width": representative.width,
                "height": representative.height,
            }
        )

    # Sort report: count desc, then file_type, then size
    report.sort(key=lambda x: (-x["count"], x["file_type"], x["file_size"]))

    return dict(grouped), report


def _thumbnail_similar(hash1: str, hash2: str, threshold: int = 5) -> bool:
    """
    Check if two thumbnail hashes are similar.

    Args:
        hash1: First hash string
        hash2: Second hash string
        threshold: Maximum hamming distance for similarity

    Returns:
        True if hashes are similar
    """
    if not hash1 or not hash2:
        return False

    # If hashes are identical, they're similar
    if hash1 == hash2:
        return True

    try:
        import imagehash

        h1 = imagehash.hex_to_hash(hash1)
        h2 = imagehash.hex_to_hash(hash2)
        distance = h1 - h2
        return distance <= threshold
    except (ImportError, ValueError, TypeError):
        # If imagehash is not available or comparison fails, only exact match
        return False

