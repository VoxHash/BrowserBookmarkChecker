# BrowserBookmarkChecker

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**BrowserBookmarkChecker** is a production-quality, cross-platform desktop application for merging and deduplicating browser bookmarks. It supports both GUI (PyQt6) and CLI interfaces, handles multiple bookmark formats, and provides intelligent URL canonicalization with optional fuzzy title matching.

## Features

### Core Functionality

- **Multi-Format Support**: Import Netscape HTML and Chrome/Chromium JSON bookmark files
- **Intelligent Deduplication**: 
  - URL canonicalization (removes tracking parameters, normalizes URLs)
  - Optional fuzzy title matching within same domain (using RapidFuzz)
  - Configurable similarity threshold (0-100)
- **Cross-Platform**: Runs on Windows, macOS, and Linux
- **Dual Interface**: 
  - **GUI**: Modern PyQt6 interface with drag & drop support
  - **CLI**: Full-featured command-line interface
- **Export Formats**:
  - Merged Netscape HTML file (compatible with all browsers)
  - CSV deduplication report with statistics
- **Multi-Language Support**: i18n support for 11 languages (English, Russian, Portuguese, Spanish, Estonian, French, German, Japanese, Chinese, Korean, Indonesian)
- **Privacy-First**: Fully offline, no telemetry, no network calls

### Technical Highlights

- **Clean Architecture**: Modular design with parsers → normalization → dedupe → merge → exporters
- **Deterministic**: Identical inputs produce identical outputs
- **Extensible**: Easy to add new parsers (Firefox .jsonlz4, Safari plist, etc.)
- **Production-Ready**: Comprehensive tests, type checking, linting, CI/CD

## Installation

### Prerequisites

- Python 3.11 or higher
- pip

### Install from Source

```bash
# Clone the repository
git clone https://github.com/VoxHashTechnologies/BrowserBookmarkChecker.git
cd BrowserBookmarkChecker

# Install dependencies
pip install -r requirements.txt

# Optional: Install in development mode with dev dependencies
pip install -e ".[dev]"
```

## Quick Start

### GUI Mode

Launch the graphical interface:

```bash
python -m bookmark_checker
```

Or use the convenience script:

```bash
./scripts/run_gui.sh
```

**GUI Features:**
1. Click **Import Files** or drag & drop bookmark files
2. Adjust **Similarity** slider (0-100, default 85)
3. Click **Find & Merge** to deduplicate
4. Review results in the table
5. Click **Export Merged** to save HTML and CSV reports

### CLI Mode

Merge bookmarks from command line:

```bash
python -m bookmark_checker \
    --input file1.html file2.json \
    --out merged_bookmarks.html \
    --similarity 85
```

**CLI Options:**
- `--input`, `-i`: Input bookmark files (HTML or JSON), multiple files allowed
- `--out`, `-o`: Output HTML file path (default: `merged_bookmarks.html`)
- `--similarity`, `-s`: Similarity threshold for fuzzy matching (0-100, default: 85)
- `--no-fuzzy`: Disable fuzzy title matching (use only canonical URL matching)

**Example:**

```bash
# Merge Chrome and Firefox exports
python -m bookmark_checker \
    --input chrome_bookmarks.html firefox_bookmarks.html \
    --out merged.html \
    --similarity 90

# Process with fuzzy matching disabled
python -m bookmark_checker \
    --input bookmarks.json \
    --out output.html \
    --no-fuzzy
```

## Usage

### Input Formats

**Netscape HTML** (`.html`):
- Exported from Chrome, Edge, Brave, Firefox, Safari
- Standard format with `<DL>`, `<DT>`, `<H3>`, `<A>` elements
- Supports folder hierarchy and `ADD_DATE` timestamps

**Chrome JSON** (`.json`):
- Chrome/Chromium `Bookmarks` file
- Located at:
  - Windows: `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Bookmarks`
  - macOS: `~/Library/Application Support/Google/Chrome/Default/Bookmarks`
  - Linux: `~/.config/google-chrome/Default/Bookmarks`

### Output Formats

**Merged HTML** (`merged_bookmarks.html`):
- Valid Netscape HTML format
- Organized by domain: `Merged/<domain>/`
- Preserves `ADD_DATE` when available
- Ready to import into any browser

**CSV Report** (`merged_bookmarks_dedupe_report.csv`):
- Columns: `canonical_url`, `title`, `count`, `example_folders`, `sources`
- Sorted by count (descending), then title (ascending)
- Shows duplicate groups and their statistics

### URL Canonicalization

The tool normalizes URLs to identify duplicates:

- **Lowercases** scheme and host
- **Removes** default ports (:80, :443)
- **Strips** URL fragments (`#section`)
- **Removes** trailing slashes on non-root paths
- **Filters** tracking parameters:
  - `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`
  - `gclid`, `fbclid`, `mc_cid`, `mc_eid`, `igshid`, `yclid`
  - `_hsenc`, `_hsmi`, `mkt_tok`, `ref`, `cmp`, `spm`, `ved`, `si`, `s`, `trk`, `scid`, `ck_subscriber_id`
- **Preserves** non-tracking query parameters

**Example:**
```
https://example.com/page?utm_source=email&id=123#section
→ https://example.com/page?id=123
```

### Fuzzy Title Matching

When enabled, the tool uses RapidFuzz to merge bookmarks with similar titles within the same domain:

- **Domain-scoped**: Only compares titles from the same domain
- **Configurable threshold**: 0-100 (default: 85)
- **Algorithm**: `partial_ratio` for flexible matching

**Example:**
- "Python Tutorial" and "Python Tutorial Guide" (same domain) → merged if similarity ≥ threshold
- "Python Tutorial" (example.com) and "Python Tutorial" (other.com) → not merged (different domains)

## Configuration

### Similarity Threshold

- **0-100**: Minimum similarity score for fuzzy title matching
- **85 (default)**: Balanced between strict and lenient
- **100**: Only exact title matches (within same domain)
- **0-50**: Very lenient (may merge unrelated bookmarks)

### Disabling Fuzzy Matching

Use `--no-fuzzy` flag (CLI) or disable in GUI to use only canonical URL matching. Useful for:
- Large datasets where fuzzy matching is slow
- When you want strict URL-based deduplication only

## Extending Parsers

To add support for new bookmark formats (e.g., Firefox `.jsonlz4`, Safari `.plist`):

1. **Create parser function** in `bookmark_checker/core/parsers.py`:

```python
def parse_firefox_jsonlz4(path: str) -> BookmarkCollection:
    """Parse Firefox jsonlz4 bookmark file."""
    # Implementation here
    pass
```

2. **Update `parse_many()`** to detect and route to new parser:

```python
def parse_many(paths: List[str]) -> BookmarkCollection:
    # ...
    if path_obj.suffix.lower() == ".jsonlz4":
        parsed = parse_firefox_jsonlz4(str(path_obj))
    # ...
```

3. **Add tests** in `tests/test_parsers.py`

4. **Update documentation**

## Building Standalone Binaries

### Nuitka (Preferred)

```bash
./scripts/build_nuitka.sh
```

Output: `dist/BrowserBookmarkChecker` (or `.exe` on Windows)

### PyInstaller (Fallback)

```bash
./scripts/build_pyinstaller.sh
```

Output: `dist/BrowserBookmarkChecker` (or `.exe` on Windows)

**Note**: Ensure icons are generated from `assets/icon.svg`:
- **Windows**: `icon.ico` (multi-size ICO file)
- **macOS**: `icon.icns` (IconSet)
- **Linux**: `icon_256.png` (PNG)

Use tools like ImageMagick, Inkscape, or online converters to generate platform-specific icons.

## Development

### Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"
```

### Code Quality

```bash
# Lint
ruff check bookmark_checker tests

# Format
black bookmark_checker tests

# Type check
mypy bookmark_checker
```

### Testing

```bash
# Run tests with coverage
pytest

# Run specific test file
pytest tests/test_utils.py

# Run with verbose output
pytest -v
```

### Project Structure

```
BrowserBookmarkChecker/
├── bookmark_checker/          # Main package
│   ├── core/                  # Core logic
│   │   ├── models.py          # Data models
│   │   ├── utils.py           # URL canonicalization
│   │   ├── parsers.py         # Bookmark parsers
│   │   ├── dedupe.py          # Deduplication
│   │   ├── merge.py           # Merging logic
│   │   └── exporters.py       # Export functions
│   ├── ui/                    # GUI
│   │   └── main_window.py     # PyQt6 window
│   ├── i18n/                  # Translations
│   ├── app.py                 # CLI entry point
│   └── __main__.py            # Module entry
├── tests/                     # Test suite
├── examples/                   # Sample data
├── assets/                     # Icons
├── scripts/                    # Build/run scripts
└── .github/workflows/         # CI/CD
```

## FAQ

### Large Files (100k+ bookmarks)

The tool is optimized for large datasets:
- Incremental processing where possible
- Efficient data structures
- Memory-conscious parsing

For very large files (500k+), consider:
- Processing in batches
- Using `--no-fuzzy` to speed up
- Increasing system RAM

### Fuzzy Matching Performance

Fuzzy matching adds computational overhead:
- **Small datasets** (<10k): Negligible impact
- **Medium datasets** (10k-50k): 2-5 seconds additional
- **Large datasets** (50k+): May take 10-30 seconds

Use `--no-fuzzy` for faster processing on large datasets.

### Import Errors

If a file fails to parse:
- Check file format (must be valid Netscape HTML or Chrome JSON)
- Verify file encoding (UTF-8)
- The tool continues processing other files (errors are logged)

### Export Format Compatibility

The exported HTML is compatible with:
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Edge
- ✅ Safari
- ✅ Brave
- ✅ Opera

### Adding New Languages

Edit `bookmark_checker/i18n/translations.py` and add translations for all keys in the `TRANSLATIONS` dictionary.

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features and improvements.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to the project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/VoxHashTechnologies/BrowserBookmarkChecker/issues)
- **Email**: contact@voxhash.dev
- **Documentation**: See `docs/` folder for detailed documentation

## Acknowledgments

- **BeautifulSoup4** for HTML parsing
- **RapidFuzz** for fuzzy string matching
- **PyQt6** for the GUI framework
- **VoxHash Technologies** for development and maintenance

---

**Version**: 1.0.0  
**Release Date**: August 29, 2025  
**Maintained by**: VoxHash Technologies

