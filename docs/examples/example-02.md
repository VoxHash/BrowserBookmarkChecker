# Example 2: Programmatic Usage

## Scenario

You want to programmatically process bookmarks using the Python API.

## Code Example

```python
from bookmark_checker.core.parsers import parse_many
from bookmark_checker.core.merge import merge_collections
from bookmark_checker.core.exporters import (
    export_netscape_html,
    export_dedupe_report_csv,
)

# Parse multiple bookmark files
collection = parse_many([
    "chrome_bookmarks.json",
    "firefox_bookmarks.html",
    "edge_bookmarks.html",
])

print(f"Loaded {len(collection)} bookmarks")

# Merge duplicates with custom similarity threshold
merged, report = merge_collections(
    collection,
    similarity_threshold=90,  # Stricter matching
    enable_fuzzy=True,
)

print(f"Merged to {len(merged)} unique bookmarks")
print(f"Found {len(report)} duplicate groups")

# Export results
export_netscape_html(merged, "merged_bookmarks.html")
export_dedupe_report_csv(report, "dedupe_report.csv")

# Analyze results
total_duplicates = sum(item["count"] - 1 for item in report)
print(f"Removed {total_duplicates} duplicate bookmarks")
```

## Advanced Usage

### Custom Processing

```python
from bookmark_checker.core.dedupe import annotate_canonical, group_duplicates
from bookmark_checker.core.utils import canonicalize_url

# Annotate with canonical URLs
annotate_canonical(collection)

# Group duplicates
grouped, report = group_duplicates(
    collection,
    similarity_threshold=85,
    enable_fuzzy=True,
)

# Process groups
for canonical_url, bookmarks in grouped.items():
    if len(bookmarks) > 1:
        print(f"Found {len(bookmarks)} duplicates for {canonical_url}")
        # Custom processing here
```

### Filtering Before Export

```python
# Filter bookmarks by domain
filtered = BookmarkCollection()
for bookmark in merged.bookmarks:
    domain = domain_from_url(bookmark.canonical_url)
    if domain.endswith(".com"):  # Only .com domains
        filtered.add(bookmark)

export_netscape_html(filtered, "filtered_bookmarks.html")
```

## Use Cases

- Batch processing multiple bookmark files
- Custom filtering and organization
- Integration with other tools
- Automated bookmark management
- Building bookmark analysis tools
