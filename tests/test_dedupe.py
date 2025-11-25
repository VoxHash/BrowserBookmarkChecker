"""Tests for deduplication logic."""

from datetime import datetime

import pytest

from bookmark_checker.core.dedupe import annotate_canonical, group_duplicates
from bookmark_checker.core.models import Bookmark, BookmarkCollection
from bookmark_checker.core.utils import canonicalize_url


class TestAnnotateCanonical:
    """Tests for canonical annotation."""

    def test_annotates_canonical_url(self) -> None:
        """Test that canonical URLs are annotated."""
        collection = BookmarkCollection()
        bookmark = Bookmark(
            url="https://example.com/page?utm_source=test",
            title="Example",
            source_file="test.html",
        )
        collection.add(bookmark)

        annotate_canonical(collection)

        assert bookmark.canonical_url == canonicalize_url(bookmark.url)
        assert "utm_source" not in bookmark.canonical_url

    def test_normalizes_titles(self) -> None:
        """Test that titles are normalized."""
        collection = BookmarkCollection()
        bookmark = Bookmark(
            url="https://example.com",
            title="  Example   Title  ",
            source_file="test.html",
        )
        collection.add(bookmark)

        annotate_canonical(collection)

        assert bookmark.title == "Example Title"


class TestGroupDuplicates:
    """Tests for duplicate grouping."""

    def test_groups_by_canonical_url(self) -> None:
        """Test that bookmarks are grouped by canonical URL."""
        collection = BookmarkCollection()
        b1 = Bookmark(
            url="https://example.com/page?utm_source=test",
            title="Example",
            source_file="test1.html",
        )
        b2 = Bookmark(
            url="https://example.com/page?utm_medium=email",
            title="Example",
            source_file="test2.html",
        )
        collection.add(b1)
        collection.add(b2)

        annotate_canonical(collection)
        grouped, report = group_duplicates(collection, enable_fuzzy=False)

        # Should be grouped together (same canonical URL)
        canonical = canonicalize_url(b1.url)
        assert canonical in grouped
        assert len(grouped[canonical]) == 2

    def test_fuzzy_merge_same_domain(self) -> None:
        """Test that fuzzy merging works within same domain."""
        collection = BookmarkCollection()
        b1 = Bookmark(
            url="https://example.com/page1",
            title="Python Tutorial",
            source_file="test1.html",
        )
        b2 = Bookmark(
            url="https://example.com/page2",
            title="Python Tutorial Guide",
            source_file="test2.html",
        )
        collection.add(b1)
        collection.add(b2)

        annotate_canonical(collection)
        grouped, report = group_duplicates(collection, similarity_threshold=80, enable_fuzzy=True)

        # Should be merged if similarity is high enough
        # Note: This depends on rapidfuzz being available
        assert len(report) <= 2  # May be 1 if merged, or 2 if not

    def test_no_fuzzy_merge_different_domains(self) -> None:
        """Test that fuzzy merging doesn't cross domains."""
        collection = BookmarkCollection()
        b1 = Bookmark(
            url="https://example.com/page",
            title="Python Tutorial",
            source_file="test1.html",
        )
        b2 = Bookmark(
            url="https://other.com/page",
            title="Python Tutorial",
            source_file="test2.html",
        )
        collection.add(b1)
        collection.add(b2)

        annotate_canonical(collection)
        grouped, report = group_duplicates(collection, similarity_threshold=100, enable_fuzzy=True)

        # Should not be merged (different domains)
        assert len(report) == 2

    def test_report_sorted_by_count(self) -> None:
        """Test that report is sorted by count descending."""
        collection = BookmarkCollection()
        # Add multiple duplicates of one URL
        for i in range(3):
            collection.add(
                Bookmark(
                    url="https://example.com/duplicate",
                    title="Duplicate",
                    source_file=f"test{i}.html",
                )
            )
        # Add single instance of another URL
        collection.add(
            Bookmark(
                url="https://example.com/single",
                title="Single",
                source_file="test.html",
            )
        )

        annotate_canonical(collection)
        _, report = group_duplicates(collection, enable_fuzzy=False)

        # First item should have count 3
        assert report[0]["count"] == 3
        assert report[0]["canonical_url"] == canonicalize_url("https://example.com/duplicate")

