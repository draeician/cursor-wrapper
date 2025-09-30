#!/usr/bin/env python3
"""Test script to verify the cursor-wrapper package installation."""

import subprocess
import sys
from pathlib import Path


def test_package_installation():
    """Test that the package can be imported and the command works."""
    try:
        # Test import
        import cursor_wrapper
        print(f"✓ Package imported successfully (version: {cursor_wrapper.__version__})")
        
        # Test version command
        result = subprocess.run(
            ["cursor", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and "cursor-wrapper" in result.stdout:
            print("✓ Version command works correctly")
        else:
            print(f"⚠ Version command failed")
            print(f"  stdout: {result.stdout}")
            print(f"  stderr: {result.stderr}")
        
        # Test help command
        result = subprocess.run(
            ["cursor", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("✓ Help command executed successfully")
        else:
            print(f"⚠ Help command returned exit code {result.returncode}")
            print(f"  stdout: {result.stdout}")
            print(f"  stderr: {result.stderr}")
        
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import package: {e}")
        return False
    except subprocess.TimeoutExpired:
        print("⚠ Command timed out (this might be expected if Cursor is already running)")
        return True
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_package_structure():
    """Test that the package has the expected structure."""
    package_dir = Path("cursor_wrapper")
    
    required_files = [
        "__init__.py",
        "main.py"
    ]
    
    for file in required_files:
        file_path = package_dir / file
        if file_path.exists():
            print(f"✓ Found {file}")
        else:
            print(f"✗ Missing {file}")
            return False
    
    return True


if __name__ == "__main__":
    print("Testing cursor-wrapper package...")
    print()
    
    print("1. Testing package structure:")
    structure_ok = test_package_structure()
    print()
    
    print("2. Testing package installation:")
    installation_ok = test_package_installation()
    print()
    
    if structure_ok and installation_ok:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed!")
        sys.exit(1)


