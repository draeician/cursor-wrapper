#!/usr/bin/env python3
"""
Main module for the Cursor wrapper application.
Converts the original bash script functionality to Python.
"""

import os
import sys
import subprocess
import signal
import time
import stat
from pathlib import Path
from typing import Optional, List


class CursorWrapper:
    """Main class for managing Cursor AppImage execution."""
    
    def __init__(self):
        self.cursor_dir = Path.home() / ".local" / "bin"
        self.cursor_symlink = self.cursor_dir / "cursor.latest"
        self.log_dir = Path.home() / ".local" / "logs" / "cursor"
        self.stdout_log = self.log_dir / "stdout.log"
        self.stderr_log = self.log_dir / "stderr.log"
        self.max_log_size = 5 * 1024 * 1024  # 5MB
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def is_cursor_running(self) -> bool:
        """Check if Cursor is already running."""
        try:
            result = subprocess.run(
                ["pgrep", "-f", str(self.cursor_symlink)],
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def rotate_logs(self, log_file: Path) -> None:
        """Rotate log files if they exceed the maximum size."""
        if log_file.exists() and log_file.stat().st_size > self.max_log_size:
            old_log = log_file.with_suffix(log_file.suffix + ".old")
            if old_log.exists():
                old_log.unlink()
            log_file.rename(old_log)
    
    def update_cursor_symlink(self) -> None:
        """Update Cursor symlink to point to the latest AppImage."""
        try:
            # Find the latest AppImage file
            appimages = list(self.cursor_dir.glob("cursor-*.AppImage"))
            if not appimages:
                print(f"Error: No Cursor AppImage found in {self.cursor_dir}", file=sys.stderr)
                sys.exit(1)
            
            # Sort by modification time (newest first)
            latest_appimage = max(appimages, key=lambda p: p.stat().st_mtime)
            
            # Update symlink if necessary
            if (not self.cursor_symlink.is_symlink() or 
                self.cursor_symlink.resolve() != latest_appimage.resolve()):
                if self.cursor_symlink.exists():
                    self.cursor_symlink.unlink()
                self.cursor_symlink.symlink_to(latest_appimage)
                print(f"Updated Cursor symlink to: {latest_appimage}")
        except (OSError, subprocess.SubprocessError) as e:
            print(f"Error updating symlink: {e}", file=sys.stderr)
            sys.exit(1)
    
    def start_cursor(self, args: List[str]) -> int:
        """Start Cursor AppImage in the background."""
        try:
            # Prepare the command
            cmd = [str(self.cursor_symlink)] + args
            
            # Open log files
            with open(self.stdout_log, 'a') as stdout_file, \
                 open(self.stderr_log, 'a') as stderr_file:
                
                # Start the process
                process = subprocess.Popen(
                    cmd,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    stdin=subprocess.DEVNULL,
                    preexec_fn=os.setsid  # Create new process group
                )
                
                print(f"Cursor started with PID {process.pid}. Logs available at:")
                print(f"  Stdout: {self.stdout_log}")
                print(f"  Stderr: {self.stderr_log}")
                
                # Wait a short time to check if the process is still running
                time.sleep(2)
                if process.poll() is None:
                    print("Cursor is running in the background.")
                    return 0
                else:
                    print("Warning: Cursor may have failed to start. Check the logs for details.")
                    return 1
                    
        except (OSError, subprocess.SubprocessError) as e:
            print(f"Error starting Cursor: {e}", file=sys.stderr)
            return 1
    
    def run(self, args: List[str]) -> int:
        """Main execution method."""
        # Update symlink if necessary
        self.update_cursor_symlink()
        
        # Check if Cursor is already running
        if self.is_cursor_running():
            print("Cursor is already running. Exiting.")
            return 0
        
        # Rotate log files if necessary
        self.rotate_logs(self.stdout_log)
        self.rotate_logs(self.stderr_log)
        
        # Start Cursor
        return self.start_cursor(args)


def show_help():
    """Show help information."""
    from cursor_wrapper import __version__
    help_text = f"""cursor-wrapper {__version__}

A wrapper script for managing Cursor AppImage execution with logging and process management.

USAGE:
    cursor [OPTIONS] [ARGS...]

OPTIONS:
    --version, -v    Show version information
    --help, -h       Show this help message

DESCRIPTION:
    This wrapper automatically manages Cursor AppImage execution by:
    - Finding the latest Cursor AppImage in ~/.local/bin/
    - Updating symlinks as needed
    - Checking for running instances to prevent duplicates
    - Starting Cursor in the background with proper logging
    - Providing status feedback

    All arguments are passed through to the Cursor application.

LOGS:
    Logs are stored in ~/.local/logs/cursor/:
    - stdout.log - Standard output
    - stderr.log - Standard error
    
    Log files are automatically rotated when they exceed 5MB.

REQUIREMENTS:
    - Cursor AppImage files in ~/.local/bin/ (named cursor-*.AppImage)
"""
    print(help_text)

def main():
    """Entry point for the application."""
    # Check for help/version flags first
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--version', '-v']:
            from cursor_wrapper import __version__
            print(f"cursor-wrapper {__version__}")
            sys.exit(0)
        elif sys.argv[1] in ['--help', '-h']:
            show_help()
            sys.exit(0)
    
    wrapper = CursorWrapper()
    args = sys.argv[1:]  # Skip the script name
    sys.exit(wrapper.run(args))


if __name__ == "__main__":
    main()


