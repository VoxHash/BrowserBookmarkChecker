"""Merge logic for selecting representative bookmarks and organizing output."""

from typing import Any

from bookmark_checker.core.models import Bookmark, BookmarkCollection
from bookmark_checker.core.utils import domain_from_url


def merge_collections(
    collection: BookmarkCollection, similarity_threshold: int = 85, enable_fuzzy: bool = True
) -> tuple[BookmarkCollection, list[dict[str, Any]]]:
    """
    Merge duplicate bookmarks, selecting representatives and organizing by domain.

    Args:
        collection: Collection to merge
        similarity_threshold: Minimum similarity score for fuzzy matching
        enable_fuzzy: Whether to enable fuzzy title matching

    Returns:
        Tuple of (merged collection, dedupe report)
    """
    from bookmark_checker.core.dedupe import annotate_canonical, group_duplicates

    # Annotate with canonical URLs
    annotate_canonical(collection)

    # Group duplicates
    grouped, report = group_duplicates(collection, similarity_threshold, enable_fuzzy)

    # Create merged collection
    merged = BookmarkCollection()

    for canonical_url, bookmarks in grouped.items():
        if not bookmarks:
            continue

        # Select representative: earliest added date, or first bookmark
        representative = bookmarks[0]
        earliest_date = representative.added

        for bookmark in bookmarks[1:]:
            if bookmark.added and (earliest_date is None or bookmark.added < earliest_date):
                representative = bookmark
                earliest_date = bookmark.added

        # Determine folder path based on domain
        domain = domain_from_url(canonical_url)
        if domain:
            folder_path = f"Merged/{domain}"
        else:
            folder_path = "Merged"

        # Create merged bookmark
        merged_bookmark = Bookmark(
            url=representative.url,
            title=representative.title,
            added=representative.added,
            folder_path=folder_path,
            source_file=", ".join(sorted(set(b.source_file for b in bookmarks if b.source_file))),
            canonical_url=canonical_url,
            meta={"original_count": len(bookmarks)},
        )

        merged.add(merged_bookmark)

    return merged, report

