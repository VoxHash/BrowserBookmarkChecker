# Browser-Bookmark Checker

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> Cross-platform desktop application for merging and deduplicating browser bookmarks with intelligent URL canonicalization and fuzzy title matching.

## ✨ Features

- **Multi-Format Support**: Import Netscape HTML and Chrome/Chromium JSON bookmark files
- **Intelligent Deduplication**: URL canonicalization removes tracking parameters and normalizes URLs
- **Fuzzy Matching**: Optional fuzzy title matching within same domain using RapidFuzz
- **Cross-Platform**: Runs on Windows, macOS, and Linux
- **Dual Interface**: Modern PyQt6 GUI with drag & drop, plus full-featured CLI
- **Multi-Language**: i18n support for 11 languages
- **Privacy-First**: Fully offline, no telemetry, no network calls

## 🧭 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Examples](#-examples)
- [Architecture](#-architecture)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Quick Start

```bash
# 1) Install
pip install -r requirements.txt

# 2) Run GUI
python -m bookmark_checker

# 3) Or use CLI
python -m bookmark_checker --input bookmarks.html --out merged.html
```

## 💿 Installation

See [docs/installation.md](docs/installation.md) for platform-specific steps.

**Prerequisites**: Python 3.11 or higher

```bash
# Clone the repository
git clone https://github.com/VoxHash/VAForge_Checker.git
cd VAForge_Checker

# Install dependencies
pip install -r requirements.txt

# Optional: Install in development mode
pip install -e ".[dev]"
```

## 🛠 Usage

### GUI Mode

Launch the graphical interface:

```bash
python -m bookmark_checker
```

**Workflow**:
1. Click **Import Files** or drag & drop bookmark files
2. Adjust **Similarity** slider (0-100, default 85)
3. Click **Find & Merge** to deduplicate
4. Review results in the table
5. Click **Export Merged** to save HTML and CSV reports

### CLI Mode

```bash
python -m bookmark_checker \
    --input file1.html file2.json \
    --out merged_bookmarks.html \
    --similarity 85
```

**Options**:
- `--input`, `-i`: Input bookmark files (HTML or JSON), multiple files allowed
- `--out`, `-o`: Output HTML file path (default: `merged_bookmarks.html`)
- `--similarity`, `-s`: Similarity threshold for fuzzy matching (0-100, default: 85)
- `--no-fuzzy`: Disable fuzzy title matching

See [docs/usage.md](docs/usage.md) and [docs/cli.md](docs/cli.md) for detailed documentation.

## ⚙️ Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| Similarity Threshold | Minimum similarity score (0-100) for fuzzy matching | 85 |
| Fuzzy Matching | Enable fuzzy title matching within same domain | Enabled |
| Export Format | Output format (HTML, CSV) | HTML + CSV |

**Similarity Threshold Guide**:
- **85 (default)**: Balanced between strict and lenient
- **100**: Only exact title matches
- **0-50**: Very lenient (may merge unrelated bookmarks)

See [docs/configuration.md](docs/configuration.md) for full configuration reference.

## 📚 Examples

- **[Basic Deduplication](docs/examples/example-01.md)** — Merge Chrome and Firefox bookmarks
- **[Programmatic Usage](docs/examples/example-02.md)** — Use the Python API
- More examples: [docs/examples/](docs/examples/)

## 🧩 Architecture

Browser-Bookmark Checker follows a modular architecture:

```
Input Files → Parsers → Normalization → Deduplication → Merge → Exporters → Output Files
```

**Key Components**:
- **Parsers**: Parse Netscape HTML and Chrome JSON formats
- **URL Canonicalization**: Remove tracking parameters, normalize URLs
- **Deduplication**: Canonical URL matching + optional fuzzy title matching
- **Merging**: Select representatives and organize by domain
- **Exporters**: Generate HTML and CSV outputs

See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

## 🗺 Roadmap

Planned milestones live in [ROADMAP.md](ROADMAP.md). For changes, see [CHANGELOG.md](CHANGELOG.md).

**Upcoming**:
- Firefox `.jsonlz4` format support
- Safari `.plist` format support
- Performance optimizations for large datasets
- Enhanced error messages and user experience

## 🤝 Contributing

We welcome PRs! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and follow the PR template.

**Quick Start**:
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint and format
ruff check bookmark_checker media_checker tests
black bookmark_checker media_checker tests
```

## 🔒 Security

Please report vulnerabilities via [SECURITY.md](SECURITY.md).

**Privacy**: This tool processes bookmark files locally and does not send data over the network or collect telemetry.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/VoxHash/VAForge_Checker/issues)
- **Email**: contact@voxhash.dev
- **FAQ**: [docs/faq.md](docs/faq.md)

See [SUPPORT.md](SUPPORT.md) for more support options.

## 🙏 Acknowledgments

- **BeautifulSoup4** for HTML parsing
- **RapidFuzz** for fuzzy string matching
- **PyQt6** for the GUI framework
- **VoxHash Technologies** for development and maintenance

---

**Version**: 1.0.0  
**Maintained by**: VoxHash Technologies
