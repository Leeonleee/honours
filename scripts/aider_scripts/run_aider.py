#!/usr/bin/env python3
"""
run_aider.py

A small convenience wrapper that invokes the ``aider`` CLI on a provided
Contributor License Agreement (CLA) file.

Usage
-----
    python scripts/aider_scripts/run_aider.py path/to/cla.txt

The script:
1. Validates exactly one CLI argument is supplied.
2. Confirms the supplied path exists.
3. Delegates execution to the ``aider`` executable, forwarding the CLA file path.
"""

import subprocess
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: run_aider.py <cla_file_path>", file=sys.stderr)
        sys.exit(1)

    cla_path = Path(sys.argv[1])

    if not cla_path.is_file():
        print(f"Error: '{cla_path}' does not exist or is not a file.", file=sys.stderr)
        sys.exit(1)

    try:
        subprocess.run(["aider", str(cla_path)], check=True)
    except FileNotFoundError:
        print(
            "Error: 'aider' executable not found. "
            "Ensure it is installed and on your PATH.",
            file=sys.stderr,
        )
        sys.exit(1)
    except subprocess.CalledProcessError as exc:
        print(f"'aider' exited with non-zero status {exc.returncode}", file=sys.stderr)
        sys.exit(exc.returncode)


if __name__ == "__main__":
    main()
