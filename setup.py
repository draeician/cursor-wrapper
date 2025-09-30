#!/usr/bin/env python3
"""Setup script for cursor-wrapper package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cursor-wrapper",
    version="1.2.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A wrapper script for managing Cursor AppImage execution with logging and process management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cursor-wrapper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Tools",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "cursor=cursor_wrapper.main:main",
        ],
    },
)


