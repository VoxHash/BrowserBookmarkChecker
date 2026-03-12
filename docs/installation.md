# Installation

## Platform-Specific Instructions

### Windows

1. Install Python 3.11+ from [python.org](https://www.python.org/downloads/)
2. Open Command Prompt or PowerShell
3. Navigate to the project directory
4. Run: `pip install -r requirements.txt`

### macOS

```bash
# Using Homebrew (recommended)
brew install python@3.11
pip3 install -r requirements.txt

# Or download from python.org
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.11 python3-pip
pip3 install -r requirements.txt
```

### Linux (Fedora/RHEL)

```bash
sudo dnf install python3.11 python3-pip
pip3 install -r requirements.txt
```

## Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Development Installation

For development with all tools:

```bash
pip install -e ".[dev]"
```

This installs:
- Core dependencies
- Development tools (ruff, black, mypy, pytest)

## Troubleshooting

- **Permission errors**: Use `pip install --user` or a virtual environment
- **Missing dependencies**: Ensure all system libraries are installed (especially for PyQt6)
- **Python version**: Ensure Python 3.11+ is installed and in PATH

See [Troubleshooting](troubleshooting.md) for more help.
