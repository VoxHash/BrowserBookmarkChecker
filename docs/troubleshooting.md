# Troubleshooting

## Common Issues

### Import Errors

**Problem**: `ModuleNotFoundError` or `ImportError`

**Solutions**:
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check Python version: `python --version` (should be 3.11+)
3. Use virtual environment to avoid conflicts
4. Reinstall dependencies: `pip install --upgrade -r requirements.txt`

### GUI Won't Start

**Problem**: GUI application doesn't launch

**Solutions**:
1. Check PyQt6 installation: `python -c "import PyQt6; print('OK')"`
2. On Linux, install system dependencies:
   ```bash
   # Ubuntu/Debian
   sudo apt install python3-pyqt6
   
   # Fedora
   sudo dnf install python3-qt6
   ```
3. Check for display server (Linux): Ensure X11 or Wayland is running
4. Try CLI mode first: `python -m bookmark_checker --input test.html`

### File Parsing Errors

**Problem**: "No bookmarks found" or parsing errors

**Solutions**:
1. Verify file format (must be Netscape HTML or Chrome JSON)
2. Check file encoding (should be UTF-8)
3. Ensure file is not corrupted
4. Try exporting bookmarks again from browser
5. Check file permissions (read access required)

### Performance Issues

**Problem**: Slow processing with large files

**Solutions**:
1. Disable fuzzy matching: `--no-fuzzy` flag
2. Process files in smaller batches
3. Increase system RAM if available
4. Close other applications to free memory
5. Use CLI mode (faster than GUI for large datasets)

### Memory Errors

**Problem**: Out of memory errors with very large files

**Solutions**:
1. Process files in batches (split large files)
2. Disable fuzzy matching to reduce memory usage
3. Increase system RAM or use a machine with more memory
4. Process one file at a time instead of multiple files

### Export Errors

**Problem**: Export fails or produces invalid files

**Solutions**:
1. Check disk space availability
2. Verify write permissions for output directory
3. Ensure output path is valid (not a directory)
4. Check for special characters in file paths
5. Try a different output location

### Fuzzy Matching Not Working

**Problem**: Similar bookmarks not being merged

**Solutions**:
1. Lower similarity threshold (try 70-80 instead of 85)
2. Ensure fuzzy matching is enabled (not using `--no-fuzzy`)
3. Check that bookmarks are from the same domain (fuzzy matching is domain-scoped)
4. Verify RapidFuzz is installed: `pip install rapidfuzz`

## Platform-Specific Issues

### Windows

- **PyQt6 installation**: May require Visual C++ redistributables
- **Path issues**: Use forward slashes or raw strings for paths
- **Permissions**: Run as administrator if file access issues occur

### macOS

- **Python version**: Use Homebrew Python or official installer
- **PyQt6**: May require Xcode Command Line Tools
- **Permissions**: Grant Terminal/iTerm full disk access if needed

### Linux

- **System dependencies**: Install `python3-pyqt6` or equivalent
- **Display server**: Ensure X11/Wayland is running for GUI
- **Permissions**: Check file permissions and ownership

## Getting Help

If you're still experiencing issues:

1. Check [FAQ](faq.md) for common questions
2. Search [GitHub Issues](https://github.com/VoxHash/BrowserBookmarkChecker/issues)
3. Review [CHANGELOG.md](../CHANGELOG.md) for recent changes
4. Open a new issue with:
   - OS and Python version
   - Error messages/logs
   - Steps to reproduce
   - Expected vs actual behavior

See [SUPPORT.md](../SUPPORT.md) for more support options.
