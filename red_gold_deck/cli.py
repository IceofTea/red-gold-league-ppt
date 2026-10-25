# -*- coding: utf-8 -*-
"""Command-line entry point: ``red-gold-deck build examples/demo.py``."""
from __future__ import annotations

import argparse
import sys

from .builder import build_from_file, load_config, validate_config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="red-gold-deck",
        description="Generate a red-gold Chinese lecture deck (PPTX + DOCX).")
    sub = parser.add_subparsers(dest="command", required=True)

    b = sub.add_parser("build", help="build PPTX and DOCX from a Python config")
    b.add_argument("config", help="path to a .py file defining CFG")
    b.add_argument("-o", "--out",
                   help="output root directory (default: cfg['out_dir'] or ./out)")

    v = sub.add_parser("validate", help="validate a config without writing files")
    v.add_argument("config")

    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            cfg = load_config(args.config)
            validate_config(cfg)
            print(f"OK: {len(cfg['pages'])} pages, types="
                  f"{sorted({p['t'] for p in cfg['pages']})}")
        else:
            build_from_file(args.config, args.out)
    except Exception as exc:  # noqa: BLE001 - CLI should print, not traceback
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
