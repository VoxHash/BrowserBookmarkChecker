"""Exporters for merged bookmark collections."""

import csv
import html
from collections import defaultdict
from typing import Any

from bookmark_checker.core.models import Bookmark, BookmarkCollection


def export_netscape_html(collection: BookmarkCollection, path: str) -> None:
    """
    Export collection to Netscape HTML format.

    Args:
        collection: Collection to export
        path: Output file path
    """
    # Group bookmarks by folder
    folder_map: dict[str, list[Bookmark]] = defaultdict(list)

    for bookmark in collection.bookmarks:
        folder_path = bookmark.folder_path or "Merged"
        folder_map[folder_path].append(bookmark)

    # Sort folders and bookmarks
    sorted_folders = sorted(folder_map.keys())
    for folder in sorted_folders:
        folder_map[folder].sort(key=lambda b: b.title.lower())

    # Write HTML
    with open(path, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE NETSCAPE-Bookmark-file-1>\n")
        f.write("<!-- This is an automatically generated file.\n")
        f.write("     It will be read and overwritten.\n")
        f.write("     DO NOT EDIT! -->\n")
        f.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n')
        f.write("<TITLE>Bookmarks</TITLE>\n")
        f.write("<H1>Bookmarks</H1>\n")
        f.write("<DL><p>\n")

        current_path_parts: list[str] = []
        current_indent = 0

        for folder_path in sorted_folders:
            bookmarks = folder_map[folder_path]
            if not bookmarks:
                continue

            folder_parts = folder_path.split("/") if folder_path else []

            # Find common prefix with current path
            common_length = 0
            for i, (part1, part2) in enumerate(zip(current_path_parts, folder_parts, strict=False)):
                if part1 == part2:
                    common_length = i + 1
                else:
                    break

            # Close folders that are no longer needed
            for _ in range(len(current_path_parts) - common_length):
                current_indent -= 1
                f.write("  " * current_indent + "</DL><p>\n")

            # Open new folders
            for i in range(common_length, len(folder_parts)):
                folder_name = folder_parts[i]
                f.write("  " * current_indent + "<DT><H3>" + html.escape(folder_name) + "</H3>\n")
                f.write("  " * current_indent + "<DL><p>\n")
                current_indent += 1

            # Write bookmarks
            for bookmark in bookmarks:
                timestamp = ""
                if bookmark.added:
                    timestamp = f' ADD_DATE="{int(bookmark.added.timestamp())}"'

                f.write(
                    "  " * current_indent
                    + f'<DT><A HREF="{html.escape(bookmark.url)}"{timestamp}>'
                    + html.escape(bookmark.title)
                    + "</A>\n"
                )

            current_path_parts = folder_parts

        # Close all remaining folders
        for _ in range(len(current_path_parts)):
            current_indent -= 1
            f.write("  " * current_indent + "</DL><p>\n")

        f.write("</DL><p>\n")


def export_dedupe_report_csv(report: list[dict[str, Any]], path: str) -> None:
    """
    Export deduplication report to CSV.

    Args:
        report: List of report dictionaries
        path: Output CSV file path
    """
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["canonical_url", "title", "count", "example_folders", "sources"],
        )
        writer.writeheader()

        for item in report:
            writer.writerow(
                {
                    "canonical_url": item["canonical_url"],
                    "title": item["title"],
                    "count": item["count"],
                    "example_folders": " | ".join(item["folders"][:5]),  # Limit to 5 examples
                    "sources": " | ".join(item["sources"]),
                }
            )

