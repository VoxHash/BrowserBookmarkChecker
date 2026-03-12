# API Reference

## Core Modules

### `bookmark_checker.core.parsers`

#### `parse_many(paths: list[str]) -> BookmarkCollection`

Parse multiple bookmark files and merge into a single collection.

**Parameters**:
- `paths`: List of file paths to parse (HTML or JSON)

**Returns**: `BookmarkCollection` with all parsed bookmarks

**Example**:
```python
from bookmark_checker.core.parsers import parse_many

collection = parse_many(["bookmarks.html", "chrome.json"])
```

#### `parse_netscape_html(path: str) -> BookmarkCollection`

Parse Netscape HTML bookmark file.

**Parameters**:
- `path`: Path to HTML file

**Returns**: `BookmarkCollection` with parsed bookmarks

#### `parse_chrome_json(path: str) -> BookmarkCollection`

Parse Chrome/Chromium JSON bookmark file.

**Parameters**:
- `path`: Path to JSON file

**Returns**: `BookmarkCollection` with parsed bookmarks

### `bookmark_checker.core.dedupe`

#### `group_duplicates(collection: BookmarkCollection, similarity_threshold: int = 85, enable_fuzzy: bool = True) -> tuple[dict[str, list[Bookmark]], list[dict[str, Any]]]`

Group duplicate bookmarks by canonical URL, with optional fuzzy title matching.

**Parameters**:
- `collection`: Collection to deduplicate
- `similarity_threshold`: Minimum similarity score (0-100) for fuzzy matching
- `enable_fuzzy`: Whether to enable fuzzy title matching within same domain

**Returns**: Tuple of (grouped dict, report list)

**Example**:
```python
from bookmark_checker.core.dedupe import group_duplicates

grouped, report = group_duplicates(collection, similarity_threshold=90)
```

#### `annotate_canonical(collection: BookmarkCollection) -> None`

Annotate bookmarks with canonical URLs and normalized titles.

**Parameters**:
- `collection`: Collection to annotate in-place

### `bookmark_checker.core.merge`

#### `merge_collections(collection: BookmarkCollection, similarity_threshold: int = 85, enable_fuzzy: bool = True) -> tuple[BookmarkCollection, list[dict[str, Any]]]`

Merge duplicate bookmarks, selecting representatives and organizing by domain.

**Parameters**:
- `collection`: Collection to merge
- `similarity_threshold`: Minimum similarity score for fuzzy matching
- `enable_fuzzy`: Whether to enable fuzzy title matching

**Returns**: Tuple of (merged collection, dedupe report)

### `bookmark_checker.core.exporters`

#### `export_netscape_html(collection: BookmarkCollection, path: str) -> None`

Export collection to Netscape HTML format.

**Parameters**:
- `collection`: Collection to export
- `path`: Output file path

#### `export_dedupe_report_csv(report: list[dict[str, Any]], path: str) -> None`

Export deduplication report to CSV.

**Parameters**:
- `report`: List of report dictionaries
- `path`: Output CSV file path

### `bookmark_checker.core.utils`

#### `canonicalize_url(url: str) -> str`

Canonicalize a URL by removing tracking parameters and normalizing.

**Parameters**:
- `url`: URL string to canonicalize

**Returns**: Canonicalized URL string

#### `domain_from_url(url: str) -> str`

Extract domain from URL.

**Parameters**:
- `url`: URL string

**Returns**: Domain string (empty if invalid)

#### `normalize_whitespace(s: str) -> str`

Normalize whitespace: collapse multiple spaces/tabs/newlines to single space.

**Parameters**:
- `s`: String to normalize

**Returns**: Normalized string

## Data Models

### `Bookmark`

Represents a single bookmark.

**Attributes**:
- `url: str` - Original URL
- `title: str` - Bookmark title
- `added: datetime | None` - Date added
- `folder_path: str` - Folder path
- `source_file: str` - Source file path
- `canonical_url: str` - Canonicalized URL
- `meta: dict[str, Any]` - Additional metadata

### `BookmarkCollection`

Collection of bookmarks with metadata.

**Methods**:
- `add(bookmark: Bookmark) -> None` - Add a bookmark
- `extend(bookmarks: list[Bookmark]) -> None` - Add multiple bookmarks
- `__len__() -> int` - Return number of bookmarks
- `__iter__() -> Iterator[Bookmark]` - Iterate over bookmarks

## Example Usage

```python
from bookmark_checker.core.parsers import parse_many
from bookmark_checker.core.merge import merge_collections
from bookmark_checker.core.exporters import export_netscape_html, export_dedupe_report_csv

# Parse bookmarks
collection = parse_many(["chrome.html", "firefox.html"])

# Merge duplicates
merged, report = merge_collections(collection, similarity_threshold=90)

# Export results
export_netscape_html(merged, "merged.html")
export_dedupe_report_csv(report, "report.csv")
```
