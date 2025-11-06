#!/usr/bin/env python

import argparse
import cProfile
import io
import os
import pstats
import sys
from pathlib import Path

import pytest


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Profile the dummy data smoke tests and write the results to convenient "
            "locations for performance investigations."
        )
    )
    parser.add_argument(
        "--output",
        default=Path("tmp/dummy_data_smoke.prof"),
        type=Path,
        help="Path to write the raw cProfile statistics (default: tmp/dummy_data_smoke.prof).",
    )
    parser.add_argument(
        "--summary",
        default=Path("tmp/dummy_data_smoke_summary.txt"),
        type=Path,
        help="Path to write a human-readable summary (default: tmp/dummy_data_smoke_summary.txt).",
    )
    parser.add_argument(
        "--sort",
        default="cumulative",
        choices=["cumulative", "time", "calls", "ncalls", "tottime"],
        help="Sort column for the summary output (default: cumulative).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=30,
        help="Number of rows to show in the textual summary (default: 30).",
    )
    parser.add_argument(
        "pytest_args",
        nargs="*",
        help="Additional arguments forwarded to pytest (for example --maxfail=1).",
    )
    return parser.parse_args(argv)


def ensure_parent(path: Path) -> None:
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    ensure_parent(args.output)
    ensure_parent(args.summary)

    os.environ.setdefault("PYTHONHASHSEED", "0")

    profiler = cProfile.Profile()
    profiler.enable()
    exit_code = pytest.main(["-m", "dummy_data_smoke", *args.pytest_args])
    profiler.disable()

    profiler.dump_stats(str(args.output))

    stats_stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stats_stream).sort_stats(args.sort)
    stats.print_stats(args.limit)

    summary_text = stats_stream.getvalue()
    if args.summary:
        args.summary.write_text(summary_text)

    sys.stdout.write(
        f"Profiling complete. Raw stats: {args.output}. Summary: {args.summary}.\n"
    )
    sys.stdout.write(f"Top entries (sorted by {args.sort}):\n{summary_text}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
