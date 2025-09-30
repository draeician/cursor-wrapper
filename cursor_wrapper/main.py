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
import requests
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse


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
        
        # Cursor download URLs and configuration
        self.cursor_download_url = "https://downloader.cursor.sh/linux/appImage/x64"
        self.cursor_filename = "cursor-latest.AppImage"
    
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
    
    def update_cursor_symlink(self, auto_install: bool = False) -> None:
        """Update Cursor symlink to point to the latest AppImage."""
        try:
            # Find the latest AppImage file
            appimages = list(self.cursor_dir.glob("cursor-*.AppImage"))
            if not appimages:
                if auto_install:
                    print(f"No Cursor AppImage found in {self.cursor_dir}")
                    print("Auto-installing latest Cursor AppImage...")
                    self.install_cursor()
                    # Try again after installation
                    appimages = list(self.cursor_dir.glob("cursor-*.AppImage"))
                    if not appimages:
                        print("Error: Installation failed, no AppImage found", file=sys.stderr)
                        sys.exit(1)
                else:
                    print(f"Error: No Cursor AppImage found in {self.cursor_dir}", file=sys.stderr)
                    print("Use --install to download and install the latest Cursor AppImage", file=sys.stderr)
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
    
    def download_cursor_appimage(self) -> Path:
        """Download the latest Cursor AppImage."""
        print("Downloading latest Cursor AppImage...")
        
        try:
            # Create a temporary file for the download
            with tempfile.NamedTemporaryFile(delete=False, suffix='.AppImage') as temp_file:
                temp_path = Path(temp_file.name)
            
            # Download the file
            response = requests.get(self.cursor_download_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rDownloading... {percent:.1f}%", end='', flush=True)
            
            print()  # New line after progress
            
            # Make the file executable
            temp_path.chmod(temp_path.stat().st_mode | stat.S_IEXEC)
            
            return temp_path
            
        except requests.RequestException as e:
            print(f"Error downloading Cursor AppImage: {e}", file=sys.stderr)
            if temp_path.exists():
                temp_path.unlink()
            sys.exit(1)
        except OSError as e:
            print(f"Error setting file permissions: {e}", file=sys.stderr)
            if temp_path.exists():
                temp_path.unlink()
            sys.exit(1)
    
    def install_cursor(self) -> None:
        """Download and install the latest Cursor AppImage."""
        print("Installing Cursor AppImage...")
        
        # Ensure the bin directory exists
        self.cursor_dir.mkdir(parents=True, exist_ok=True)
        
        # Download the AppImage
        temp_path = self.download_cursor_appimage()
        
        try:
            # Generate a unique filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_path = self.cursor_dir / f"cursor-{timestamp}.AppImage"
            
            # Move the downloaded file to the final location
            shutil.move(str(temp_path), str(final_path))
            
            print(f"Cursor AppImage installed to: {final_path}")
            
            # Update the symlink
            self.update_cursor_symlink()
            
        except OSError as e:
            print(f"Error installing Cursor AppImage: {e}", file=sys.stderr)
            if temp_path.exists():
                temp_path.unlink()
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
    
    def run(self, args: List[str], auto_install: bool = False) -> int:
        """Main execution method."""
        # Update symlink if necessary
        self.update_cursor_symlink(auto_install=auto_install)
        
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
    --install        Download and install the latest Cursor AppImage

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
    # Check for help/version/install flags first
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--version', '-v']:
            from cursor_wrapper import __version__
            print(f"cursor-wrapper {__version__}")
            sys.exit(0)
        elif sys.argv[1] in ['--help', '-h']:
            show_help()
            sys.exit(0)
        elif sys.argv[1] == '--install':
            wrapper = CursorWrapper()
            wrapper.install_cursor()
            print("Installation complete. You can now run 'cursor' to start the application.")
            sys.exit(0)
    
    wrapper = CursorWrapper()
    args = sys.argv[1:]  # Skip the script name
    sys.exit(wrapper.run(args, auto_install=True))


if __name__ == "__main__":
    main()


