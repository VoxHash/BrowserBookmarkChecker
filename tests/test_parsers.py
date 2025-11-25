"""Tests for bookmark parsers."""

import tempfile
from pathlib import Path

from bookmark_checker.core.parsers import parse_chrome_json, parse_many, parse_netscape_html


class TestParseNetscapeHTML:
    """Tests for Netscape HTML parser."""

    def test_parses_basic_bookmark(self) -> None:
        """Test parsing a basic bookmark."""
        html = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<DL><p>
<DT><A HREF="https://example.com">Example</A>
</DL><p>"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write(html)
            temp_path = f.name

        try:
            collection = parse_netscape_html(temp_path)
            assert len(collection.bookmarks) == 1
            assert collection.bookmarks[0].url == "https://example.com"
            assert collection.bookmarks[0].title == "Example"
        finally:
            Path(temp_path).unlink()

    def test_parses_folder_structure(self) -> None:
        """Test parsing folder hierarchy."""
        html = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<DL><p>
<DT><H3>Folder1</H3>
<DL><p>
<DT><A HREF="https://example.com">Example</A>
</DL><p>
</DL><p>"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write(html)
            temp_path = f.name

        try:
            collection = parse_netscape_html(temp_path)
            assert len(collection.bookmarks) == 1
            assert collection.bookmarks[0].folder_path == "Folder1"
        finally:
            Path(temp_path).unlink()

    def test_parses_add_date(self) -> None:
        """Test parsing ADD_DATE attribute."""
        html = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<DL><p>
<DT><A HREF="https://example.com" ADD_DATE="1609459200">Example</A>
</DL><p>"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write(html)
            temp_path = f.name

        try:
            collection = parse_netscape_html(temp_path)
            assert len(collection.bookmarks) == 1
            assert collection.bookmarks[0].added is not None
        finally:
            Path(temp_path).unlink()


class TestParseChromeJSON:
    """Tests for Chrome JSON parser."""

    def test_parses_basic_bookmark(self) -> None:
        """Test parsing a basic bookmark."""
        json_data = {
            "roots": {
                "bookmark_bar": {
                    "children": [
                        {
                            "type": "url",
                            "name": "Example",
                            "url": "https://example.com",
                            "date_added": "13254192000000000",
                        }
                    ],
                }
            }
        }
        import json

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(json_data, f)
            temp_path = f.name

        try:
            collection = parse_chrome_json(temp_path)
            assert len(collection.bookmarks) == 1
            assert collection.bookmarks[0].url == "https://example.com"
            assert collection.bookmarks[0].title == "Example"
        finally:
            Path(temp_path).unlink()

    def test_parses_folder_structure(self) -> None:
        """Test parsing folder hierarchy."""
        json_data = {
            "roots": {
                "bookmark_bar": {
                    "children": [
                        {
                            "type": "folder",
                            "name": "Folder1",
                            "children": [
                                {
                                    "type": "url",
                                    "name": "Example",
                                    "url": "https://example.com",
                                }
                            ],
                        }
                    ],
                }
            }
        }
        import json

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(json_data, f)
            temp_path = f.name

        try:
            collection = parse_chrome_json(temp_path)
            assert len(collection.bookmarks) == 1
            assert "Folder1" in collection.bookmarks[0].folder_path
        finally:
            Path(temp_path).unlink()


class TestParseMany:
    """Tests for parsing multiple files."""

    def test_parses_multiple_files(self) -> None:
        """Test parsing multiple files."""
        html1 = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<DL><p>
<DT><A HREF="https://example.com">Example</A>
</DL><p>"""
        html2 = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<DL><p>
<DT><A HREF="https://test.com">Test</A>
</DL><p>"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f1:
            f1.write(html1)
            temp_path1 = f1.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f2:
            f2.write(html2)
            temp_path2 = f2.name

        try:
            collection = parse_many([temp_path1, temp_path2])
            assert len(collection.bookmarks) == 2
        finally:
            Path(temp_path1).unlink()
            Path(temp_path2).unlink()

