"""Deduplication logic with fuzzy title matching."""

from collections import defaultdict
from typing import TYPE_CHECKING, Any

from bookmark_checker.core.models import Bookmark, BookmarkCollection
from bookmark_checker.core.utils import domain_from_url, normalize_whitespace

if TYPE_CHECKING:
    from rapidfuzz import fuzz as fuzz_module
else:
    try:
        from rapidfuzz import fuzz as fuzz_module
    except ImportError:
        fuzz_module = None

fuzz = fuzz_module


def annotate_canonical(collection: BookmarkCollection) -> None:
    """
    Annotate bookmarks with canonical URLs and normalized titles.

    Args:
        collection: Collection to annotate in-place
    """
    from bookmark_checker.core.utils import canonicalize_url

    for bookmark in collection.bookmarks:
        bookmark.canonical_url = canonicalize_url(bookmark.url)
        bookmark.title = normalize_whitespace(bookmark.title)


def group_duplicates(
    collection: BookmarkCollection, similarity_threshold: int = 85, enable_fuzzy: bool = True
) -> tuple[dict[str, list[Bookmark]], list[dict[str, Any]]]:
    """
    Group duplicate bookmarks by canonical URL, with optional fuzzy title matching.

    Args:
        collection: Collection to deduplicate
        similarity_threshold: Minimum similarity score (0-100) for fuzzy matching
        enable_fuzzy: Whether to enable fuzzy title matching within same domain

    Returns:
        Tuple of (grouped dict, report list)
        - grouped: dict mapping canonical_url to list of Bookmark objects
        - report: list of dicts with dedupe statistics
    """
    # Primary grouping by canonical URL
    grouped: dict[str, list[Bookmark]] = defaultdict(list)

    for bookmark in collection.bookmarks:
        key = bookmark.canonical_url or bookmark.url
        grouped[key].append(bookmark)

    # Fuzzy merge within same domain if enabled
    if enable_fuzzy and fuzz is not None:
        # Group by domain first
        domain_groups: dict[str, dict[str, list[Bookmark]]] = defaultdict(dict)

        for canonical_url, bookmarks in grouped.items():
            if not bookmarks:
                continue
            domain = domain_from_url(canonical_url)
            domain_groups[domain][canonical_url] = bookmarks

        # Merge groups within same domain based on title similarity
        merged_grouped: dict[str, list[Bookmark]] = {}
        consumed_keys: set[str] = set()

        for _domain, domain_urls in domain_groups.items():
            domain_canonicals = list(domain_urls.keys())

            for i, canonical_a in enumerate(domain_canonicals):
                if canonical_a in consumed_keys:
                    continue

                group_a = domain_urls[canonical_a]
                if not group_a:
                    continue

                # Representative title from group A
                title_a = group_a[0].title

                # Try to merge with other groups in same domain
                merged_bookmarks = group_a.copy()

                for j, canonical_b in enumerate(domain_canonicals):
                    if i >= j or canonical_b in consumed_keys:
                        continue

                    group_b = domain_urls[canonical_b]
                    if not group_b:
                        continue

                    title_b = group_b[0].title

                    # Check similarity
                    similarity = fuzz.partial_ratio(title_a.lower(), title_b.lower())

                    if similarity >= similarity_threshold:
                        # Merge groups
                        merged_bookmarks.extend(group_b)
                        consumed_keys.add(canonical_b)

                merged_grouped[canonical_a] = merged_bookmarks
                consumed_keys.add(canonical_a)

        # Add unmerged groups from other domains
        for canonical_url, bookmarks in grouped.items():
            if canonical_url not in consumed_keys:
                merged_grouped[canonical_url] = bookmarks

        grouped = merged_grouped

    # Generate report
    report: list[dict[str, Any]] = []

    for canonical_url, bookmarks in grouped.items():
        if not bookmarks:
            continue

        # Get unique folders and sources
        folders = sorted(set(b.folder_path for b in bookmarks if b.folder_path))
        sources = sorted(set(b.source_file for b in bookmarks if b.source_file))

        # Representative title (use first bookmark's title)
        title = bookmarks[0].title if bookmarks else ""

        report.append(
            {
                "canonical_url": canonical_url,
                "title": title,
                "count": len(bookmarks),
                "folders": folders,
                "sources": sources,
            }
        )

    # Sort report: count desc, title asc
    report.sort(key=lambda x: (-x["count"], x["title"].lower()))

    return dict(grouped), report
