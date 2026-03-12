# Usage Guide

## GUI Mode

### Basic Workflow

1. **Launch**: `python -m bookmark_checker`
2. **Import**: Click "Import Files" or drag & drop bookmark files
3. **Configure**: Adjust similarity slider (0-100)
4. **Process**: Click "Find & Merge"
5. **Export**: Click "Export Merged" to save results

### Advanced Features

- **Language Selection**: Choose from 11 supported languages
- **Drag & Drop**: Drop bookmark files directly onto the window
- **Progress Indicators**: Monitor processing progress
- **Table View**: Review duplicate groups and statistics

## CLI Mode

### Basic Command

```bash
python -m bookmark_checker \
    --input file1.html file2.json \
    --out merged_bookmarks.html \
    --similarity 85
```

### Options

- `--input`, `-i`: Input bookmark files (HTML or JSON), multiple files allowed
- `--out`, `-o`: Output HTML file path (default: `merged_bookmarks.html`)
- `--similarity`, `-s`: Similarity threshold for fuzzy matching (0-100, default: 85)
- `--no-fuzzy`: Disable fuzzy title matching

### Examples

**Merge Chrome and Firefox exports:**
```bash
python -m bookmark_checker \
    --input chrome_bookmarks.html firefox_bookmarks.html \
    --out merged.html \
    --similarity 90
```

**Process with strict URL matching only:**
```bash
python -m bookmark_checker \
    --input bookmarks.json \
    --out output.html \
    --no-fuzzy
```

## Input Formats

### Netscape HTML (`.html`)
- Exported from Chrome, Edge, Brave, Firefox, Safari
- Standard format with `<DL>`, `<DT>`, `<H3>`, `<A>` elements
- Supports folder hierarchy and `ADD_DATE` timestamps

### Chrome JSON (`.json`)
- Chrome/Chromium `Bookmarks` file
- Located at:
  - Windows: `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Bookmarks`
  - macOS: `~/Library/Application Support/Google/Chrome/Default/Bookmarks`
  - Linux: `~/.config/google-chrome/Default/Bookmarks`

## Output Formats

### Merged HTML
- Valid Netscape HTML format
- Organized by domain: `Merged/<domain>/`
- Preserves `ADD_DATE` when available
- Ready to import into any browser

### CSV Report
- Columns: `canonical_url`, `title`, `count`, `example_folders`, `sources`
- Sorted by count (descending), then title (ascending)
- Shows duplicate groups and their statistics

## Configuration

### Similarity Threshold
- **0-100**: Minimum similarity score for fuzzy title matching
- **85 (default)**: Balanced between strict and lenient
- **100**: Only exact title matches (within same domain)
- **0-50**: Very lenient (may merge unrelated bookmarks)

### Fuzzy Matching
- Enabled by default
- Uses RapidFuzz for domain-scoped title comparison
- Can be disabled with `--no-fuzzy` flag for faster processing

See [Configuration](configuration.md) for advanced options.
