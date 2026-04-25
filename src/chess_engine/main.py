"""Command-line entry point for the learning scaffold."""

from __future__ import annotations

import argparse
from typing import List, Optional


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Chess engine learning scaffold")
    parser.add_argument("--version", action="store_true", help="Show that the scaffold is installed")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print("chess-engine scaffold")
        return 0

    parser.print_help()
    print("\nImplement the CLI in src/chess_engine/main.py as you build the engine.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

