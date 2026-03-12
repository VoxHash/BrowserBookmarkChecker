# Quick Start

Get Browser-Bookmark Checker running in minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/VoxHash/BrowserBookmarkChecker.git
cd BrowserBookmarkChecker

# Install dependencies
pip install -r requirements.txt
```

## GUI Mode

Launch the graphical interface:

```bash
python -m bookmark_checker
```

Or use the convenience script:

```bash
./scripts/run_gui.sh
```

**Quick Steps:**
1. Click **Import Files** or drag & drop bookmark files
2. Adjust **Similarity** slider (0-100, default 85)
3. Click **Find & Merge** to deduplicate
4. Review results in the table
5. Click **Export Merged** to save HTML and CSV reports

## CLI Mode

Merge bookmarks from command line:

```bash
python -m bookmark_checker \
    --input file1.html file2.json \
    --out merged_bookmarks.html \
    --similarity 85
```

## Next Steps

- Read the [Usage Guide](usage.md) for detailed workflows
- Check [Examples](examples/) for common use cases
- See [Configuration](configuration.md) for advanced options
