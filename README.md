# Cursor Wrapper

A Python wrapper for managing Cursor AppImage execution with logging and process management.

## Features

- Automatic symlink management to the latest Cursor AppImage
- Process management to prevent multiple instances
- Log rotation to prevent excessive disk usage
- Background execution with proper logging
- pipx installable package

## Installation

Install using pipx:

```bash
pipx install cursor-wrapper
```

## Usage

After installation, you can use the `cursor` command just like the original script:

```bash
cursor [options]
```

The wrapper will:

1. Check for the latest Cursor AppImage in `~/.local/bin/`
2. Update the symlink if necessary
3. Check if Cursor is already running
4. Start Cursor in the background with proper logging
5. Provide feedback about the process status

## Logs

Logs are stored in `~/.local/logs/cursor/`:

- `stdout.log` - Standard output
- `stderr.log` - Standard error

Log files are automatically rotated when they exceed 5MB.

## Requirements

- Python 3.8+
- Cursor AppImage files in `~/.local/bin/` (named `cursor-*.AppImage`)
