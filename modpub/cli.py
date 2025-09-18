"""Command line entrypoint for modpub.

Usage:
    modpub sync --from <source> --to <dest>

Examples:
    modpub sync --from thingiverse:123456 --to localdir:/path
    modpub sync --from localdir:/path --to thingiverse:new
"""
from __future__ import annotations
import argparse
import logging
from typing import Optional

from .utils import setup_logging
from .plugins import load_plugin
from .core.model import Design

LOGGER = logging.getLogger("modpub")


def _parse_locator(s: str) -> tuple[str, str]:
    """Parse a locator string "plugin:detail" into (plugin, detail)."""
    if ":" not in s:
        raise ValueError("Locator must be of the form 'plugin:detail'")
    name, detail = s.split(":", 1)
    return name, detail


def cmd_sync(ns: argparse.Namespace) -> int:
    setup_logging()
    src_name, src_detail = _parse_locator(ns.from_)
    dst_name, dst_detail = _parse_locator(ns.to)

    src = load_plugin(src_name)
    dst = load_plugin(dst_name)

    LOGGER.info("Reading from %s:%s", src_name, src_detail)
    design: Design = src.read(src_detail)

    mode = "create" if dst_detail == "new" else "update"
    if dst_name == "localdir":
        # localdir doesn't use "new" sentinel; treat empty path as error
        mode = "create" if dst_detail else "create"

    LOGGER.info("Writing to %s:%s (mode=%s)", dst_name, dst_detail, mode)
    locator_after = dst.write(design, dst_detail, mode=mode)  # type: ignore[arg-type]

    print(f"{dst_name}:{locator_after}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="modpub", description="3D model publisher")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("sync", help="Sync from a source to a destination")
    sp.add_argument("--from", dest="from_", required=True,
                    help="Source locator e.g. thingiverse:123456 or localdir:/path")
    sp.add_argument("--to", dest="to", required=True,
                    help="Destination locator e.g. localdir:/path or thingiverse:new")
    sp.set_defaults(func=cmd_sync)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    ns = parser.parse_args(argv)
    return ns.func(ns)

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
