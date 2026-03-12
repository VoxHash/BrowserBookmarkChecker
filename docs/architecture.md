# Architecture

## Overview

Browser-Bookmark Checker follows a modular architecture with clear separation of concerns:

```
Input Files → Parsers → Normalization → Deduplication → Merge → Exporters → Output Files
```

## Core Components

### Parsers (`bookmark_checker/core/parsers.py`)

- **Responsibility**: Parse different bookmark file formats
- **Supported Formats**: Netscape HTML, Chrome JSON
- **Extensibility**: Easy to add new parsers (Firefox `.jsonlz4`, Safari `.plist`)

### URL Canonicalization (`bookmark_checker/core/utils.py`)

- **Responsibility**: Normalize URLs for duplicate detection
- **Features**:
  - Remove tracking parameters
  - Normalize scheme and host
  - Strip fragments and default ports
  - Preserve non-tracking parameters

### Deduplication (`bookmark_checker/core/dedupe.py`)

- **Responsibility**: Identify duplicate bookmarks
- **Strategies**:
  1. Canonical URL matching (primary)
  2. Fuzzy title matching within same domain (optional)
- **Algorithm**: RapidFuzz `partial_ratio` for fuzzy matching

### Merging (`bookmark_checker/core/merge.py`)

- **Responsibility**: Select representative bookmarks and organize output
- **Selection**: Earliest `ADD_DATE` or first bookmark
- **Organization**: By domain (`Merged/<domain>/`)

### Exporters (`bookmark_checker/core/exporters.py`)

- **Responsibility**: Export results in various formats
- **Formats**: Netscape HTML, CSV report

## GUI Architecture

### Main Window (`bookmark_checker/ui/main_window.py`)

- **Framework**: PyQt6
- **Features**:
  - Drag & drop support
  - Multi-language support (11 languages)
  - Progress indicators
  - Dark theme

### Threading

- **ScanThread**: Background scanning of directories
- **MetadataThread**: Background metadata extraction
- Prevents UI freezing during long operations

## Data Flow

1. **Parse**: Read bookmark files → `BookmarkCollection`
2. **Annotate**: Add canonical URLs → Updated `BookmarkCollection`
3. **Group**: Identify duplicates → `dict[str, list[Bookmark]]`
4. **Merge**: Select representatives → `BookmarkCollection`
5. **Export**: Write to files → HTML + CSV

## Design Principles

- **Modularity**: Each component has a single responsibility
- **Extensibility**: Easy to add new parsers and exporters
- **Determinism**: Identical inputs produce identical outputs
- **Performance**: Efficient algorithms for large datasets
- **Privacy**: Fully offline, no network calls

## Dependencies

- **PyQt6**: GUI framework
- **BeautifulSoup4**: HTML parsing
- **RapidFuzz**: Fuzzy string matching
- **Standard Library**: `urllib.parse`, `pathlib`, `dataclasses`

## Testing

- **Unit Tests**: `tests/test_*.py`
- **Coverage**: Aim for 85%+ coverage
- **Tools**: pytest, pytest-cov

## Future Improvements

- Plugin system for custom parsers
- Caching layer for metadata
- Database backend for large-scale operations
- REST API for programmatic access
