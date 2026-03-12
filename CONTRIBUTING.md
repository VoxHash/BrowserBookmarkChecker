# Contributing to Browser-Bookmark Checker

Thanks for helping improve Browser-Bookmark Checker!

## Code of Conduct

Please read and follow our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Development Setup

```bash
# Clone the repository
git clone https://github.com/VoxHash/BrowserBookmarkChecker.git
cd BrowserBookmarkChecker

# Install dependencies
pip install -r requirements.txt

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=bookmark_checker --cov-report=term-missing
```

## Code Quality

Before submitting a PR, ensure:

```bash
# Lint code
ruff check bookmark_checker tests

# Format code
black bookmark_checker tests

# Type check
mypy bookmark_checker
```

## Branching & Commit Style

- **Branches**: `feature/...`, `fix/...`, `docs/...`, `chore/...`
- **Commits**: Use [Conventional Commits](https://www.conventionalcommits.org/):
  - `feat:` New feature
  - `fix:` Bug fix
  - `docs:` Documentation changes
  - `refactor:` Code refactoring
  - `test:` Adding or updating tests
  - `chore:` Maintenance tasks

## Pull Requests

- Link related issues in the PR description
- Add tests for new features or bug fixes
- Update documentation as needed
- Keep diffs focused and reviewable
- Follow the PR template in `.github/PULL_REQUEST_TEMPLATE.md`

## Testing

- Write tests for new functionality
- Ensure all tests pass: `pytest`
- Maintain or improve test coverage
- Test both GUI and CLI interfaces when applicable

## Release Process

- We follow [Semantic Versioning](https://semver.org/)
- Update [CHANGELOG.md](CHANGELOG.md) with all changes
- Tag releases with version numbers (e.g., `v1.0.0`)

## Project Structure

```
BrowserBookmarkChecker/
├── bookmark_checker/      # Bookmark deduplication tool
│   ├── core/             # Core logic (parsers, dedupe, merge, exporters)
│   ├── ui/               # PyQt6 GUI
│   └── i18n/             # Translations
├── tests/                # Test suite
├── examples/             # Sample data files
├── scripts/              # Build and run scripts
└── docs/                 # Documentation
```

## Questions?

- Open an issue for bugs or feature requests
- Check [SUPPORT.md](SUPPORT.md) for support options
- Email: contact@voxhash.dev
