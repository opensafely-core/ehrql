#!/usr/bin/env python3
import json
import mmap
import re
import sys
import time
from pathlib import Path


EHRQL_RE = re.compile(
    rb"(Running setup query|Running query|Fetching batch|lob_logical)"
)
COHORTEXTRACTOR_RE = re.compile(rb"\[cohortextractor\.")

# Match any sequence of seven or more digits or commas which must be preceded by a
# character which is not a digit or a period (to avoid matching digits after the point
# in floating point numbers)
NUMERAL_RE = re.compile(rb"[^\d\.]([\d,]{7,})\b")


def count_matching_numerals(filename):
    count = 0
    unique = set()
    start = time.monotonic()
    with filename.open("r+b") as f:
        contents = mmap.mmap(f.fileno(), 0)
        for match in NUMERAL_RE.finditer(contents):
            num = int(match.group(1).replace(b",", b""))
            count += 1
            unique.add(num)
    scan_time = time.monotonic() - start
    return count, len(unique), scan_time


for arg in sys.argv[1:]:
    filename = Path(arg)
    with filename.open("r+b") as f:
        chunk = f.read(16384)

    if EHRQL_RE.search(chunk):
        action_type = "ehrql"
    elif COHORTEXTRACTOR_RE.search(chunk):
        action_type = "cohortextractor"
    else:
        action_type = "analysis"

    size_bytes = filename.stat().st_size

    if 0 < size_bytes < 100 * 10**6:
        count, unique_count, scan_time = count_matching_numerals(filename)
    else:
        count, unique_count, scan_time = None, None, None

    print(
        json.dumps(
            {
                "file": str(filename),
                "type": action_type,
                "size_bytes": size_bytes,
                "numeral_count": count,
                "unique_numerals": unique_count,
                "numeral_scan_time": scan_time,
            }
        )
    )
