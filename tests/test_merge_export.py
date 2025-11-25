"""Tests for merge and export functionality."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from bookmark_checker.core.exporters import export_dedupe_report_csv, export_netscape_html
from bookmark_checker.core.merge import merge_collections
from bookmark_checker.core.models import Bookmark, BookmarkCollection


class TestMergeCollections:
    """Tests for collection merging."""

    def test_chooses_earliest_added(self) -> None:
        """Test that earliest added bookmark is chosen as representative."""
        collection = BookmarkCollection()
        now = datetime.now()
        b1 = Bookmark(
            url="https://example.com/page",
            title="Example",
            added=now,
            source_file="test1.html",
        )
        b2 = Bookmark(
            url="https://example.com/page?utm_source=test",
            title="Example",
            added=now - timedelta(days=1),
            source_file="test2.html",
        )
        collection.add(b1)
        collection.add(b2)

        merged, _ = merge_collections(collection, enable_fuzzy=False)

        assert len(merged.bookmarks) == 1
        # Representative should be the earlier one
        assert merged.bookmarks[0].added == b2.added

    def test_organizes_by_domain(self) -> None:
        """Test that merged bookmarks are organized by domain."""
        collection = BookmarkCollection()
        b1 = Bookmark(
            url="https://example.com/page1",
            title="Example 1",
            source_file="test.html",
        )
        b2 = Bookmark(
            url="https://test.com/page1",
            title="Test 1",
            source_file="test.html",
        )
        collection.add(b1)
        collection.add(b2)

        merged, _ = merge_collections(collection, enable_fuzzy=False)

        assert len(merged.bookmarks) == 2
        domains = {b.folder_path for b in merged.bookmarks}
        assert "Merged/example.com" in domains
        assert "Merged/test.com" in domains


class TestExportNetscapeHTML:
    """Tests for Netscape HTML export."""

    def test_exports_valid_html(self) -> None:
        """Test that exported HTML is valid."""
        collection = BookmarkCollection()
        collection.add(
            Bookmark(
                url="https://example.com",
                title="Example",
                folder_path="Merged/example.com",
                source_file="test.html",
            )
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            temp_path = f.name

        try:
            export_netscape_html(collection, temp_path)

            # Read and verify
            with open(temp_path, encoding="utf-8") as f:
                content = f.read()
                assert "NETSCAPE-Bookmark-file-1" in content
                assert "https://example.com" in content
                assert "Example" in content
        finally:
            Path(temp_path).unlink()

    def test_escapes_html_entities(self) -> None:
        """Test that HTML entities are escaped."""
        collection = BookmarkCollection()
        collection.add(
            Bookmark(
                url="https://example.com/page?q=test&id=1",
                title="Test & Example < >",
                folder_path="Merged/example.com",
                source_file="test.html",
            )
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            temp_path = f.name

        try:
            export_netscape_html(collection, temp_path)

            with open(temp_path, encoding="utf-8") as f:
                content = f.read()
                assert "&amp;" in content or "&lt;" in content or "&gt;" in content
        finally:
            Path(temp_path).unlink()

    def test_includes_add_date(self) -> None:
        """Test that ADD_DATE is included when available."""
        collection = BookmarkCollection()
        added = datetime.now()
        collection.add(
            Bookmark(
                url="https://example.com",
                title="Example",
                added=added,
                folder_path="Merged/example.com",
                source_file="test.html",
            )
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            temp_path = f.name

        try:
            export_netscape_html(collection, temp_path)

            with open(temp_path, encoding="utf-8") as f:
                content = f.read()
                assert "ADD_DATE" in content
        finally:
            Path(temp_path).unlink()


class TestExportCSV:
    """Tests for CSV report export."""

    def test_exports_csv_report(self) -> None:
        """Test that CSV report is exported correctly."""
        report = [
            {
                "canonical_url": "https://example.com",
                "title": "Example",
                "count": 2,
                "folders": ["Folder1", "Folder2"],
                "sources": ["test1.html", "test2.html"],
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_path = f.name

        try:
            export_dedupe_report_csv(report, temp_path)

            # Verify file exists and has content
            assert Path(temp_path).exists()
            with open(temp_path, encoding="utf-8") as f:
                content = f.read()
                assert "canonical_url" in content
                assert "Example" in content
                assert "2" in content
        finally:
            Path(temp_path).unlink()
