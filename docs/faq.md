# FAQ

## General

### What is Browser-Bookmark Checker?

Browser-Bookmark Checker is a cross-platform desktop application for merging and deduplicating browser bookmarks. It supports both GUI and CLI interfaces and handles multiple bookmark formats.

### Is it free and open source?

Yes, Browser-Bookmark Checker is open source and free to use under the MIT License.

### Does it send my data anywhere?

No. All processing is done locally on your machine. The tool is fully offline and does not make any network calls.

### What browsers are supported?

The tool can import bookmarks from:
- Chrome/Chromium (JSON format)
- Firefox (HTML export)
- Edge (HTML export)
- Safari (HTML export)
- Brave (HTML export)
- Opera (HTML export)

## Usage

### How do I export bookmarks from my browser?

**Chrome/Chromium**:
- Copy the `Bookmarks` file from:
  - Windows: `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Bookmarks`
  - macOS: `~/Library/Application Support/Google/Chrome/Default/Bookmarks`
  - Linux: `~/.config/google-chrome/Default/Bookmarks`

**Firefox/Edge/Safari**:
- Use browser's export feature (usually in Bookmarks menu)
- Export as HTML file

### What similarity threshold should I use?

- **85 (default)**: Good balance for most users
- **90-100**: Stricter matching, fewer false positives
- **70-80**: More lenient, may merge similar but different bookmarks
- **0-50**: Very lenient, use with caution

Start with 85 and adjust based on results.

### Should I enable fuzzy matching?

Yes, unless:
- Processing very large datasets (100k+ bookmarks)
- You want strict URL-based deduplication only
- Performance is critical

Fuzzy matching improves duplicate detection by comparing similar titles.

### How long does processing take?

- **Small datasets** (<10k bookmarks): < 1 second
- **Medium datasets** (10k-50k): 1-5 seconds
- **Large datasets** (50k+): 5-30 seconds (with fuzzy matching)

Use `--no-fuzzy` for faster processing on large datasets.

## Technical

### What Python version do I need?

Python 3.11 or higher is required.

### Can I use it programmatically?

Yes, see [API Reference](api.md) for programmatic usage examples.

### How do I add support for a new bookmark format?

See the "Extending Parsers" section in [README.md](../README.md) or check the parser implementation in `bookmark_checker/core/parsers.py`.

### Why are some bookmarks not merged?

Possible reasons:
1. URLs are different after canonicalization
2. Titles are not similar enough (if fuzzy matching enabled)
3. Bookmarks are from different domains (fuzzy matching is domain-scoped)
4. Similarity threshold is too high

Try lowering the similarity threshold or checking the canonical URLs.

## Troubleshooting

### The GUI won't start

See [Troubleshooting Guide](troubleshooting.md) for platform-specific solutions. Common causes:
- Missing PyQt6 dependencies
- Display server issues (Linux)
- Python version incompatibility

### I get "No bookmarks found"

- Verify file format (must be Netscape HTML or Chrome JSON)
- Check file encoding (should be UTF-8)
- Ensure file is not corrupted
- Try exporting bookmarks again from browser

### Processing is very slow

- Disable fuzzy matching with `--no-fuzzy`
- Process files in smaller batches
- Close other applications to free memory
- Use CLI mode (faster than GUI)

### Memory errors with large files

- Process files in batches
- Disable fuzzy matching
- Increase system RAM
- Process one file at a time

## Contributing

### How can I contribute?

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines. We welcome:
- Bug reports
- Feature requests
- Code contributions
- Documentation improvements

### Where do I report bugs?

Use the [bug report template](https://github.com/VoxHash/VAForge_Checker/issues/new?template=bug_report.md) on GitHub.

### How do I suggest a feature?

Use the [feature request template](https://github.com/VoxHash/VAForge_Checker/issues/new?template=feature_request.md) on GitHub.

## More Questions?

- Check [Troubleshooting Guide](troubleshooting.md)
- See [SUPPORT.md](../SUPPORT.md) for support options
- Open an issue on GitHub
- Email: contact@voxhash.dev
