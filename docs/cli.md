# CLI Reference

## Command Syntax

```bash
python -m bookmark_checker [OPTIONS]
```

## Options

### `--input`, `-i`

Input bookmark files (HTML or JSON). Multiple files allowed.

```bash
--input file1.html file2.json file3.html
```

**Required**: Yes (unless launching GUI)

### `--out`, `-o`

Output HTML file path.

```bash
--out merged_bookmarks.html
```

**Default**: `merged_bookmarks.html`

### `--similarity`, `-s`

Similarity threshold for fuzzy matching (0-100).

```bash
--similarity 90
```

**Default**: `85`

**Range**: `0` (very lenient) to `100` (exact match only)

### `--no-fuzzy`

Disable fuzzy title matching. Use only canonical URL matching.

```bash
--no-fuzzy
```

**Default**: Fuzzy matching enabled

## Examples

### Basic Merge

```bash
python -m bookmark_checker \
    --input bookmarks.html \
    --out merged.html
```

### Multiple Files with Custom Similarity

```bash
python -m bookmark_checker \
    --input chrome.html firefox.html edge.html \
    --out all_merged.html \
    --similarity 90
```

### Strict URL Matching Only

```bash
python -m bookmark_checker \
    --input bookmarks.json \
    --out output.html \
    --no-fuzzy
```

### High Similarity Threshold

```bash
python -m bookmark_checker \
    --input bookmarks.html \
    --out strict_merged.html \
    --similarity 95
```

## Exit Codes

- `0`: Success
- `1`: Error (invalid arguments, file not found, etc.)

## Output Files

The tool generates two output files:

1. **HTML file** (specified with `--out`): Merged bookmarks in Netscape format
2. **CSV file** (auto-generated): Deduplication report with `_dedupe_report.csv` suffix

Example:
- `--out merged.html` → `merged.html` and `merged_dedupe_report.csv`

## Error Handling

- **Invalid files**: Skipped with warning, processing continues
- **Missing files**: Error message, exit code 1
- **Invalid arguments**: Error message with usage help
- **Processing errors**: Error message with details

## Performance

- **Small datasets** (<10k): < 1 second
- **Medium datasets** (10k-50k): 1-5 seconds
- **Large datasets** (50k+): 5-30 seconds (with fuzzy matching)

Use `--no-fuzzy` for faster processing on large datasets.
