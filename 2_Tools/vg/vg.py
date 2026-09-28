#!/usr/bin/env python3
"""vg: the AI Videographer command-line tool. Run from the workspace root:

    python3 2_Tools/vg/vg.py --help
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vglib.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
