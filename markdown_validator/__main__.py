#!/usr/bin/env python3
"""
markdown-validator

Usage: python3 -m markdown_validator <my_markdown_document.md>

Checks for broken links and other common mistakes in Markdown files.
"""

import sys
import logging

from . import Markdown

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) != 2 or sys.argv[1] in ["--help", "-h"]:
        print(f"Usage: python3 {sys.argv[0]} <my_document.md>")
        sys.exit(1)

    filename_arg = sys.argv[1]
    md = Markdown(filename_arg)
    md_warnings = md.analyze_file()
    for w in md_warnings:
        print(w)
