# Example 1: Basic Bookmark Deduplication

## Scenario

You have bookmarks exported from Chrome and Firefox, and want to merge them while removing duplicates.

## Steps

### 1. Export Bookmarks

**From Chrome**:
- Copy `Bookmarks` file from `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Bookmarks`
- Rename to `chrome_bookmarks.json`

**From Firefox**:
- Bookmarks → Show All Bookmarks → Import and Backup → Export Bookmarks to HTML
- Save as `firefox_bookmarks.html`

### 2. Run Browser-Bookmark Checker

**GUI Mode**:
```bash
python -m bookmark_checker
```

1. Click "Import Files"
2. Select both `chrome_bookmarks.json` and `firefox_bookmarks.html`
3. Adjust similarity slider to 85 (default)
4. Click "Find & Merge"
5. Review results in table
6. Click "Export Merged"
7. Save as `merged_bookmarks.html`

**CLI Mode**:
```bash
python -m bookmark_checker \
    --input chrome_bookmarks.json firefox_bookmarks.html \
    --out merged_bookmarks.html \
    --similarity 85
```

### 3. Import Back to Browser

1. Open your browser's bookmark manager
2. Import bookmarks from `merged_bookmarks.html`
3. Verify duplicates are removed

## Expected Results

- Duplicate bookmarks merged into single entries
- CSV report showing duplicate groups
- Bookmarks organized by domain
- Original folder structure preserved where possible

## Output Files

- `merged_bookmarks.html` - Cleaned bookmarks ready to import
- `merged_bookmarks_dedupe_report.csv` - Report of duplicates found
