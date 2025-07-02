#!/usr/bin/env python3
"""
Parses an ehrQL log file (supplied either on stdin or as a filename argument) and writes
JSON lines to stdin in a format suitable for ingesting as OpenTelemetry records
"""

import fileinput
import json
import re
from collections import defaultdict


LOG_PREFIX = "[info   ] "

# Gets populated by the `@register_parser` decorator below
PARSER_DISPATCH = {}


def main():
    log_lines = extract_log_lines_with_timestamps(fileinput.input())
    log_records = (parse_log_line(*log_line) for log_line in log_lines)
    log_records = (record for record in log_records if record["type"] != "unknown")
    log_groups = group_log_records(log_records)
    otel_records = format_groups_for_otel(log_groups)

    for record in otel_records:
        print(json.dumps(record))


def register_parser(regex_str):
    regex = re.compile(regex_str, re.DOTALL)

    def register(fn):
        PARSER_DISPATCH[regex] = fn
        return fn

    return register


@register_parser(r"^Running query (\d+) / (\d+)")
def parse_query_start(match):
    return {
        "type": "query_start",
        "query_seq": int(match.group(1)),
        "query_total_count": int(match.group(2)),
    }


@register_parser("^SQL:\n(.*)")
def parse_sql(match):
    sql = match.group(1)
    return {
        "type": "sql",
        "sql": sql,
        "sql_type": get_sql_type(sql),
    }


def get_sql_type(sql):
    if sql.startswith("SELECT * INTO"):
        return "select_into"
    elif sql.startswith("CREATE TABLE"):
        return "create_table"
    elif sql.startswith("INSERT INTO"):
        return "insert"
    elif sql.startswith("CREATE CLUSTERED INDEX"):
        return "create_index"
    elif sql.startswith("DROP TABLE"):
        return "drop_table"
    else:
        assert False, f"Unknown SQL type: {sql}"


@register_parser(r"^(\d+) seconds: (.*) query_id=.*$")
def parse_cpu_stats(match):
    attrs = {
        k: float(v) if "." in v else int(v)
        for k, v in [word.partition("=")[::2] for word in match.group(2).split()]
    }
    return {
        "type": "cpu_stats",
        "elapsed_s": int(match.group(1)),
        **attrs,
    }


@register_parser(r"^scans ")
def parse_io_stats(match):
    text = match.string
    rows = [line.split() for line in text.splitlines()]
    data = [dict(zip(rows[0], row)) for row in rows[1:]]
    return {"type": "io_stats", "text": text, "data": data}


@register_parser(r"^Fetching results from query (\d+) / (\d+)")
def parse_fetch_start(match):
    return {
        "type": "fetch_start",
        "query_seq": int(match.group(1)),
        "query_total_count": int(match.group(2)),
    }


@register_parser(r"^Fetching batch (\d+)$")
def parse_batch_start(match):
    return {
        "type": "batch_start",
        "batch_seq": int(match.group(1)),
    }


@register_parser(r"^Retrying query ")
def parse_retry_query(match):
    return {
        "type": "retry_query",
    }


@register_parser(r"^Fetch complete, total rows:")
def parse_fetch_complete(match):
    return {
        "type": "fetch_complete",
    }


def extract_log_lines_with_timestamps(lines):
    next_timestamp = None
    next_lines = []
    for line in lines:
        line = line.strip()
        timestamp, _, line = line.partition(" ")
        text = line[len(LOG_PREFIX) :]
        if line.startswith(LOG_PREFIX):
            if next_timestamp is not None:
                yield next_timestamp, "\n".join(next_lines)
            next_timestamp = timestamp
            next_lines = [text]
        else:
            next_lines.append(text)
    if next_timestamp is not None:
        yield next_timestamp, "\n".join(next_lines)


def parse_log_line(timestamp, text):
    for regex, parser in PARSER_DISPATCH.items():
        if match := regex.search(text):
            record = parser(match)
            break
    else:
        record = {"type": "unknown", "text": text}
    record["timestamp"] = timestamp
    return record


def group_log_records(records):
    group = defaultdict(list)
    for record in records:
        if record["type"] in ("query_start", "fetch_start"):
            if group:
                yield group
            group = defaultdict(list)
            group["type"] = record["type"]
        group[record["type"]].append(record)
    if group:
        yield group


def format_groups_for_otel(log_groups):
    for group in log_groups:
        if group["type"] == "query_start":
            yield format_for_otel_query(group)
        elif group["type"] == "fetch_start":
            yield format_for_otel_fetch(group)
        else:
            assert False, f"Unhandled group type: {group['type']}"


def format_for_otel_query(group):
    prefix = "query"

    query_start = get_one(group["query_start"])
    sql = get_one(group["sql"])
    cpu_stats = get_one(group["cpu_stats"])
    if group["io_stats"]:
        io_stats = get_one(group["io_stats"])
        io_attrs = get_io_stats_attributes(prefix, io_stats["data"])
    else:
        io_stats = None
        io_attrs = {}

    return {
        "name": "query",
        "start": query_start["timestamp"],
        "end": cpu_stats["timestamp"],
        "attributes": {
            f"{prefix}.sql_type": sql["sql_type"],
            f"{prefix}.seq": query_start["query_seq"],
            f"{prefix}.total_count": query_start["query_total_count"],
            **{
                f"{prefix}.{k}": v
                for k, v in cpu_stats.items()
                if k not in ("type", "timestamp")
            },
            **io_attrs,
        },
        "text_attributes": {
            f"{prefix}.sql": sql["sql"],
            **({f"{prefix}.io_stats": io_stats["text"]} if io_stats else {}),
        },
    }


def get_io_stats_attributes(prefix, io_stats_data):
    tables_used = []
    attrs = {}
    for item in io_stats_data:
        tables_used.append(item["table"])
        table_name = item["table"].replace("#", "")
        for key in ("scans", "logical", "physical", "read_ahead"):
            value = int(item[key])
            attrs[f"{prefix}.table.{table_name}.{key}"] = value
    attrs[f"{prefix}.tables_used"] = tables_used
    attrs[f"{prefix}.tables_used.count"] = len(tables_used)
    return attrs


def format_for_otel_fetch(group):
    prefix = "fetch"

    fetch_start = get_one(group["fetch_start"])
    fetch_complete = get_one(group["fetch_complete"])
    batch_count = max((i["batch_seq"] for i in group["batch_start"]), default=0)
    retry_count = len(group["retry_query"])

    return {
        "name": "fetch",
        "start": fetch_start["timestamp"],
        "end": fetch_complete["timestamp"],
        "attributes": {
            f"{prefix}.batch_count": batch_count,
            f"{prefix}.retry_count": retry_count,
            "query.seq": fetch_start["query_seq"],
            "query.total_count": fetch_start["query_total_count"],
        },
    }


def get_one(lst):
    assert len(lst) == 1, f"Expected one item in {lst}"
    return lst[0]


if __name__ == "__main__":
    main()
