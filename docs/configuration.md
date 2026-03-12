# Configuration

## Similarity Threshold

Controls how similar bookmark titles must be to be considered duplicates.

| Value | Behavior |
|-------|----------|
| 0-50 | Very lenient, may merge unrelated bookmarks |
| 85 (default) | Balanced between strict and lenient |
| 90-99 | Strict matching |
| 100 | Only exact title matches |

**Recommendation**: Start with 85 and adjust based on results.

## Fuzzy Matching

Fuzzy matching compares bookmark titles within the same domain using RapidFuzz.

- **Enabled by default**: Provides better duplicate detection
- **Domain-scoped**: Only compares titles from the same domain
- **Algorithm**: Uses `partial_ratio` for flexible matching
- **Performance**: Adds 2-30 seconds depending on dataset size

**Disable when**:
- Processing very large datasets (100k+ bookmarks)
- You want strict URL-based deduplication only
- Performance is critical

## URL Canonicalization

The tool automatically normalizes URLs to identify duplicates:

- **Lowercases** scheme and host
- **Removes** default ports (:80, :443)
- **Strips** URL fragments (`#section`)
- **Removes** trailing slashes on non-root paths
- **Filters** tracking parameters (utm_*, gclid, fbclid, etc.)
- **Preserves** non-tracking query parameters

**Example**:
```
https://example.com/page?utm_source=email&id=123#section
→ https://example.com/page?id=123
```

## Export Options

### HTML Export
- Format: Netscape HTML (compatible with all browsers)
- Organization: By domain (`Merged/<domain>/`)
- Preserves: `ADD_DATE` timestamps when available

### CSV Export
- Format: CSV with UTF-8 encoding
- Columns: `canonical_url`, `title`, `count`, `example_folders`, `sources`
- Sorting: By count (descending), then title (ascending)

## Performance Tuning

### Large Datasets (100k+ bookmarks)

1. **Disable fuzzy matching**: Use `--no-fuzzy` flag
2. **Process in batches**: Split large files
3. **Increase system RAM**: For very large files (500k+)

### Memory Usage

- Typical: 50-200 MB for 10k bookmarks
- Large: 500 MB - 2 GB for 100k+ bookmarks
- Monitor with system tools if processing very large files

## Language Settings

The GUI supports 11 languages:
- English, Russian, Portuguese, Spanish, Estonian
- French, German, Japanese, Chinese, Korean, Indonesian

Change language via the dropdown in the GUI. CLI always uses English.
