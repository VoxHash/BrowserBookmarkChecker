# Release Instructions

## Creating the First Release (v1.0.0)

### Prerequisites
- All changes committed
- CI tests passing
- CHANGELOG.md updated

### Steps

1. **Commit all changes**:
   ```bash
   git add .
   git commit -m "chore: prepare v1.0.0 release"
   ```

2. **Create and push the tag**:
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0 - Initial release"
   git push origin main
   git push origin v1.0.0
   ```

3. **GitHub Release**:
   - The release workflow (`.github/workflows/release.yml`) will automatically:
     - Build distribution packages for Windows, macOS, and Linux
     - Create a GitHub release with release notes
     - Upload distribution artifacts

### Manual Release (if needed)

If you prefer to create the release manually:

1. Go to GitHub repository → Releases → Draft a new release
2. Tag: `v1.0.0`
3. Title: `v1.0.0 - Initial Release`
4. Description: Copy from `CHANGELOG.md` v1.0.0 section
5. Upload distribution files from `dist/` directory
6. Publish release

### After Release

- Update `pyproject.toml` version for next development cycle
- Move Unreleased changes in CHANGELOG.md to new version section
- Continue development on `main` or `develop` branch
