"""CLI entry point for MediaDuplicateChecker."""

import argparse
import sys
from pathlib import Path

from media_checker.core.dedupe import group_duplicates
from media_checker.core.exporters import (
    export_duplicate_list_txt,
    export_duplicate_report_csv,
    export_duplicate_report_json,
)
from media_checker.core.metadata import extract_all_metadata
from media_checker.core.scanner import scan_directory


def main() -> None:
    """Main entry point for CLI and GUI launcher."""
    parser = argparse.ArgumentParser(
        description="MediaDuplicateChecker - Find duplicate video and audio files"
    )
    parser.add_argument(
        "--folder",
        "-f",
        help="Folder to scan for media files",
        default=None,
    )
    parser.add_argument(
        "--out",
        "-o",
        help="Output report file path",
        default="duplicate_report.csv",
    )
    parser.add_argument(
        "--format",
        choices=["csv", "json", "txt"],
        help="Output format (default: csv)",
        default="csv",
    )
    parser.add_argument(
        "--tolerance",
        "-t",
        type=float,
        help="Duration tolerance in seconds (default: 1.0)",
        default=1.0,
    )
    parser.add_argument(
        "--no-hash",
        action="store_true",
        help="Disable hash-based matching",
    )
    parser.add_argument(
        "--no-size-duration",
        action="store_true",
        help="Disable size+duration matching",
    )
    parser.add_argument(
        "--no-thumbnail",
        action="store_true",
        help="Disable thumbnail-based matching for videos",
    )

    args = parser.parse_args()

    # If no folder specified, launch GUI
    if not args.folder:
        try:
            from media_checker.ui.main_window import launch_gui

            launch_gui()
        except ImportError:
            print("GUI dependencies not available. Install PyQt6 to use the GUI.")
            sys.exit(1)
        return

    # CLI mode
    try:
        folder_path = Path(args.folder)
        if not folder_path.exists() or not folder_path.is_dir():
            print(f"Error: '{args.folder}' is not a valid directory.", file=sys.stderr)
            sys.exit(1)

        print(f"Scanning directory: {folder_path}")
        collection = scan_directory(folder_path)

        if not collection.files:
            print("No media files found in the specified directory.")
            sys.exit(0)

        print(f"Found {len(collection.files)} media files")

        print("Extracting metadata...")
        for idx, media_file in enumerate(collection.files):
            extract_all_metadata(media_file, calculate_hash=True)
            if (idx + 1) % 10 == 0:
                print(f"  Processed {idx + 1}/{len(collection.files)} files...", end="\r")

        print(f"\nExtracted metadata for {len(collection.files)} files")

        print("Finding duplicates...")
        grouped, report = group_duplicates(
            collection,
            match_by_hash=not args.no_hash,
            match_by_size_duration=not args.no_size_duration,
            match_by_thumbnail=not args.no_thumbnail,
            duration_tolerance=args.tolerance,
        )

        if not report:
            print("No duplicates found.")
            sys.exit(0)

        print(f"Found {len(report)} duplicate groups")

        # Export report
        output_path = Path(args.out)
        if args.format == "json":
            if not output_path.suffix == ".json":
                output_path = output_path.with_suffix(".json")
            export_duplicate_report_json(report, str(output_path))
        elif args.format == "txt":
            if not output_path.suffix == ".txt":
                output_path = output_path.with_suffix(".txt")
            export_duplicate_list_txt(report, str(output_path))
        else:
            if not output_path.suffix == ".csv":
                output_path = output_path.with_suffix(".csv")
            export_duplicate_report_csv(report, str(output_path))

        print(f"Exported duplicate report to {output_path}")

    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

