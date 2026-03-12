# Changelog — Browser-Bookmark Checker

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CI/CD workflows for automated testing and releases
- Comprehensive documentation structure (docs/)
- GitHub issue and PR templates
- Security policy and code of conduct

### Changed
- Updated `.gitignore` with comprehensive patterns
- Improved CI workflow for bookmark_checker package
- Removed `media_checker` package (separate project)
- Updated repository URLs to `https://github.com/VoxHash/BrowserBookmarkChecker`

## [1.0.0] - 2026-03-12

### Added
- Initial release of Browser-Bookmark Checker
- Cross-platform desktop application for merging and deduplicating browser bookmarks
- GUI (PyQt6) and CLI interfaces
- Support for Netscape HTML and Chrome/Chromium JSON bookmark formats
- Intelligent URL canonicalization (removes tracking parameters, normalizes URLs)
- Optional fuzzy title matching within same domain using RapidFuzz
- Configurable similarity threshold (0-100)
- Multi-language support (11 languages: English, Russian, Portuguese, Spanish, Estonian, French, German, Japanese, Chinese, Korean, Indonesian)
- Export formats: Merged Netscape HTML and CSV deduplication report
- Drag & drop support in GUI
- Accessibility improvements: tooltips and accessible names for UI controls
- Comprehensive test suite
- Type checking with mypy
- Code formatting with black and ruff

### Fixed
- Missing dependency declarations for rapidfuzz and beautifulsoup4
- Package configuration mismatch in setuptools
- Type checking configuration updated for all dependencies
- Python compatibility (removed `strict=False` from zip)
