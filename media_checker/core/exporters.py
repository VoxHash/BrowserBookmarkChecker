"""Exporters for duplicate reports."""

import csv
import json
from pathlib import Path
from typing import Any


def export_duplicate_report_csv(report: list[dict[str, Any]], path: str) -> None:
    """
    Export duplicate report to CSV.

    Args:
        report: List of report dictionaries
        path: Output CSV file path
    """
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "group_key",
                "file_type",
                "count",
                "file_size",
                "duration",
                "codec",
                "width",
                "height",
                "paths",
                "parent_dirs",
            ],
        )
        writer.writeheader()

        for item in report:
            writer.writerow(
                {
                    "group_key": item["group_key"],
                    "file_type": item["file_type"],
                    "count": item["count"],
                    "file_size": item["file_size"],
                    "duration": item.get("duration") or "",
                    "codec": item.get("codec") or "",
                    "width": item.get("width") or "",
                    "height": item.get("height") or "",
                    "paths": " | ".join(item["paths"]),
                    "parent_dirs": " | ".join(item["parent_dirs"][:5]),  # Limit to 5 examples
                }
            )


def export_duplicate_report_json(report: list[dict[str, Any]], path: str) -> None:
    """
    Export duplicate report to JSON.

    Args:
        report: List of report dictionaries
        path: Output JSON file path
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def export_duplicate_list_txt(report: list[dict[str, Any]], path: str) -> None:
    """
    Export duplicate list to plain text.

    Args:
        report: List of report dictionaries
        path: Output text file path
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write("Media Duplicate Report\n")
        f.write("=" * 80 + "\n\n")

        for item in report:
            f.write(f"Group: {item['group_key']}\n")
            f.write(f"Type: {item['file_type']}\n")
            f.write(f"Count: {item['count']}\n")
            f.write(f"Size: {item['file_size']} bytes\n")
            if item.get("duration"):
                f.write(f"Duration: {item['duration']:.2f}s\n")
            if item.get("codec"):
                f.write(f"Codec: {item['codec']}\n")
            if item.get("width") and item.get("height"):
                f.write(f"Resolution: {item['width']}x{item['height']}\n")
            f.write("\nFiles:\n")
            for file_path in item["paths"]:
                f.write(f"  - {file_path}\n")
            f.write("\n" + "-" * 80 + "\n\n")

