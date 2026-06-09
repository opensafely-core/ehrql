#!/usr/bin/env python
import sys
from datetime import datetime


def filter_lines(lines):
    skip_phrases = ("Error closing cursor",)
    for line in lines:
        if not line.strip():
            continue
        if any(phrase in line for phrase in skip_phrases):
            continue
        yield line


def get_gaps(lines):
    for i, line in enumerate(lines):
        if "Fetching results from query 002 / 003" not in line:
            continue

        prev_line = lines[i - 1]
        assert "Finished running query 001 / 003" in prev_line

        query_001_finished_at = float(prev_line.split()[0])
        query_002_starting_at = float(line.split()[0])
        gap = query_002_starting_at - query_001_finished_at

        next_line = lines[i + 1]
        errored = "TrinoUserError(type=USER_ERROR, name=TABLE_NOT_FOUND" in next_line

        timestamp = datetime.fromtimestamp(query_002_starting_at).strftime(
            "%H:%M:%S.%f"
        )
        yield timestamp, query_002_starting_at, gap, errored


def summarise(gaps):
    total = len(gaps)
    total_errored = sum(1 for _, _, _, e in gaps if e)
    print(f"Total: {total}, Errored: {total_errored} ({total_errored / total:.1%})")
    print()
    print(f"{'Time':>15}  {'Epoch':>17}  {'Gap (s)':>10}  {'Errored':>7}")
    print(f"{'-' * 15}  {'-' * 17}  {'-' * 10}  {'-' * 7}")
    for timestamp, epoch, gap, errored in sorted(gaps, key=lambda x: x[2]):
        print(f"{timestamp:>15}  {epoch:>17.6f}  {gap:>10.6f}  {errored}")


if __name__ == "__main__":
    log_file = sys.argv[1]
    with open(log_file) as f:
        lines = list(filter_lines(f.readlines()))
    gaps = list(get_gaps(lines))
    summarise(gaps)
