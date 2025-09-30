# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pipx (recommended) or pip
- Cursor AppImage files in `~/.local/bin/` (named `cursor-*.AppImage`)

## Installation Methods

### Method 1: Using pipx (Recommended)

```bash
# Install pipx if you don't have it
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install the package
pipx install cursor-wrapper
```

### Method 2: Using pip

```bash
# Install in user directory
pip install --user cursor-wrapper

# Or install in a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install cursor-wrapper
```

### Method 3: Install from source

```bash
# Clone the repository
git clone <repository-url>
cd cursor-wrapper

# Install in development mode
pip install -e .

# Or build and install
python -m build
pip install dist/cursor_wrapper-*.whl
```

## Verification

After installation, verify that the package works:

```bash
# Test the command
cursor --help

# Or run the test script
python test_installation.py
```

## Usage

Once installed, you can use the `cursor` command just like the original bash script:

```bash
cursor [options]
```

The wrapper will automatically:
- Find the latest Cursor AppImage
- Update symlinks as needed
- Check for running instances
- Start Cursor in the background with logging
- Provide status feedback

## Uninstallation

### Using pipx:
```bash
pipx uninstall cursor-wrapper
```

### Using pip:
```bash
pip uninstall cursor-wrapper
```


