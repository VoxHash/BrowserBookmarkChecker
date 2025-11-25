"""CLI entry point for BrowserBookmarkChecker."""

import argparse
import sys
from pathlib import Path

from bookmark_checker.core.exporters import export_dedupe_report_csv, export_netscape_html
from bookmark_checker.core.merge import merge_collections
from bookmark_checker.core.parsers import parse_many


def main() -> None:
    """Main entry point for CLI and GUI launcher."""
    parser = argparse.ArgumentParser(
        description="BrowserBookmarkChecker - Merge and deduplicate browser bookmarks"
    )
    parser.add_argument(
        "--input",
        "-i",
        nargs="+",
        help="Input bookmark files (HTML or JSON)",
        default=None,
    )
    parser.add_argument(
        "--out",
        "-o",
        help="Output HTML file path",
        default="merged_bookmarks.html",
    )
    parser.add_argument(
        "--similarity",
        "-s",
        type=int,
        help="Similarity threshold for fuzzy matching (0-100)",
        default=85,
    )
    parser.add_argument(
        "--no-fuzzy",
        action="store_true",
        help="Disable fuzzy title matching",
    )

    args = parser.parse_args()

    # If no input files, launch GUI
    if not args.input:
        try:
            from bookmark_checker.ui.main_window import launch_gui

            launch_gui()
        except ImportError:
            print("GUI dependencies not available. Install PyQt6 to use the GUI.")
            sys.exit(1)
        return

    # CLI mode
    try:
        # Parse input files
        collection = parse_many(args.input)

        if not collection.bookmarks:
            print("No bookmarks found in input files.")
            sys.exit(1)

        print(f"Parsed {len(collection.bookmarks)} bookmarks from {len(args.input)} file(s)")

        # Merge and deduplicate
        merged, report = merge_collections(
            collection, similarity_threshold=args.similarity, enable_fuzzy=not args.no_fuzzy
        )

        print(f"Merged to {len(merged.bookmarks)} unique bookmarks")

        # Export HTML
        output_path = Path(args.out)
        export_netscape_html(merged, str(output_path))
        print(f"Exported merged bookmarks to {output_path}")

        # Export CSV report
        csv_path = output_path.with_suffix("").with_name(f"{output_path.stem}_dedupe_report.csv")
        export_dedupe_report_csv(report, str(csv_path))
        print(f"Exported deduplication report to {csv_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
