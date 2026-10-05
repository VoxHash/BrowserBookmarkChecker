# Changelog — Browser-Bookmark Checker

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.1] - 2026-10-05

### Fixed
- Packaging: include full `bookmark_checker` package tree (`core/`, `ui/`, `i18n/`) in sdist and wheel via recursive setuptools discovery (v1.1.0 wheels omitted subpackages)
- Release assets: name macOS binary from detected architecture (`macos-arm64` on current `macos-latest`) instead of hardcoding `macos-x64`
- Release workflow: flatten PyInstaller/wheel artifacts before attaching them to GitHub Releases
- macOS app bundle: set `CFBundleShortVersionString` / `CFBundleVersion` from `pyproject.toml` when a `.app` is produced

## [1.1.0] - 2026-10-05

### Added
- Cross-platform executable builds (Linux, macOS, Windows) in the release workflow via PyInstaller (`34edb71`)
- Unit tests for `Bookmark` equality/hashing and `BookmarkCollection` length/iteration to keep coverage above the project gate

### Changed
- Repository hygiene: ignore `coverage.xml`, `.ruff_cache/`, and PyInstaller `*.spec` artifacts
- Roadmap realigned to late-2026 priorities (formats, UX polish, export options)
- Version bump to 1.1.0 across `pyproject.toml` and package metadata

### Fixed
- CI: Node.js 24 setup and `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` to silence Actions warnings (`25157a5`, `a85b516`)
- Ruff B905: pass `strict=False` to `zip()` (`7261066`)
- Black formatting across GUI translation call sites (`fa67e9f`, `048d340`, `6bbf571`, `a1de80b`, `e211a22`)
- CI workflow updates for test reliability (`3224cad`)

### Removed
- Stray `DEVELOPMENT_GOALS.md` outside the documentation kit
- Obsolete `RELEASE.md` and leftover `media_checker` package references (`99e7e7c`, `d2f2ae9`)

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

[Unreleased]: https://github.com/VoxHash/BrowserBookmarkChecker/compare/v1.1.1...HEAD
[1.1.1]: https://github.com/VoxHash/BrowserBookmarkChecker/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/VoxHash/BrowserBookmarkChecker/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/VoxHash/BrowserBookmarkChecker/releases/tag/v1.0.0
