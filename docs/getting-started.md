# Getting Started

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

## Setup

```bash
# Clone the repository
git clone https://github.com/VoxHash/VAForge_Checker.git
cd VAForge_Checker

# Install dependencies
pip install -r requirements.txt

# Optional: Install in development mode with dev dependencies
pip install -e ".[dev]"
```

## Verify Installation

```bash
# Check Python version
python --version  # Should be 3.11 or higher

# Test import
python -c "import bookmark_checker; print('OK')"
```

## Running the Application

### GUI Mode

```bash
python -m bookmark_checker
```

### CLI Mode

```bash
python -m bookmark_checker --input bookmarks.html --out merged.html
```

## First Steps

1. **Export bookmarks** from your browser (Chrome, Firefox, etc.)
2. **Import files** into Browser-Bookmark Checker
3. **Adjust settings** (similarity threshold, fuzzy matching)
4. **Merge and deduplicate**
5. **Export** the cleaned bookmarks

See [Usage Guide](usage.md) for detailed instructions.
