#!/usr/bin/env python3
"""
Parses an ehrQL log file (supplied either on stdin or as a filename argument) and writes
JSON lines to stdin in a format suitable for ingesting as OpenTelemetry records
"""

import fileinput
import json
import re
from collections import defaultdict


TIMESTAMP_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{9}Z) (.*)$")
LOG_PREFIX = "[info   ] "

# Gets populated by the `@register_parser` decorator below
PARSER_DISPATCH = {}


def main():
    for record in parse_logs(fileinput.input()):
        print(json.dumps(record))


def parse_logs(input_lines):
    log_lines = extract_log_lines_with_timestamps(input_lines)
    log_records = (parse_log_line(*log_line) for log_line in log_lines)
    log_records = (record for record in log_records if record["type"] != "unknown")
    log_groups = group_log_records(log_records)
    otel_records = format_groups_for_otel(log_groups)
    yield from otel_records


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
    if sql.startswith("SELECT * INTO [##results"):
        return "select_into_results"
    elif sql.startswith("SELECT * INTO"):
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


@register_parser(r"^Traceback \(most recent call last\):")
def parse_exception(match):
    name, args = get_exception_name_and_args(match.string)
    return {
        "type": "exception",
        "exception_type": name,
        "message": args,
        "stacktrace": match.string,
    }


def get_exception_name_and_args(text):
    for line in text.splitlines():
        if not line or line.startswith("Traceback") or line.startswith("  "):
            continue
        name, _, args = line.partition(": ")
        return name, args


def extract_log_lines_with_timestamps(lines):
    next_timestamp = None
    next_lines = []
    found_exception = False
    for timestamp, text in extract_timestamps(lines):
        if text.startswith("Traceback (most recent call last):"):
            found_exception = True
            break

        indented_text = text[len(LOG_PREFIX) :]
        if text.startswith(LOG_PREFIX):
            if next_timestamp is not None:
                yield next_timestamp, "\n".join(next_lines)
            next_timestamp = timestamp
            next_lines = [indented_text]
        else:
            next_lines.append(indented_text)

    if next_timestamp is not None:
        yield next_timestamp, "\n".join(next_lines)

    if found_exception:
        remaining_text = [t for _, t in extract_timestamps(lines)]
        yield timestamp, "\n".join([text] + remaining_text)


def extract_timestamps(lines):
    for line in lines:
        match = TIMESTAMP_RE.match(line)
        if not match:
            continue

        timestamp = match.group(1)
        text = match.group(2)
        yield timestamp, text


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
                # Support peeking forward at the next record when handling a group
                group["next_record"] = record
                yield group
            group = defaultdict(list)
            group["type"] = record["type"]
        group[record["type"]].append(record)
    if group:
        group["next_record"] = None
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

    if group["cpu_stats"]:
        cpu_stats = get_one(group["cpu_stats"])
        success = True
        end_timestamp = cpu_stats["timestamp"]
        cpu_attrs = {
            f"{prefix}.{k}": v
            for k, v in cpu_stats.items()
            if k not in ("type", "timestamp")
        }
    else:
        success = False
        end_timestamp = (
            group["next_record"]["timestamp"] if group["next_record"] else None
        )
        cpu_attrs = {}

    if group["io_stats"]:
        io_attrs = get_io_stats_attributes(prefix, get_one(group["io_stats"]))
    else:
        io_attrs = {}

    if group["exception"]:
        success = False
        if end_timestamp is None:
            end_timestamp = group["exception"][0]["timestamp"]
        events = [format_for_otel_exception(exc) for exc in group["exception"]]
    else:
        events = []

    return {
        "name": sql["sql_type"],
        "start": query_start["timestamp"],
        "end": end_timestamp,
        "attributes": {
            f"{prefix}.success": success,
            f"{prefix}.sql": sql["sql"],
            f"{prefix}.seq": query_start["query_seq"],
            f"{prefix}.total_count": query_start["query_total_count"],
            **cpu_attrs,
            **io_attrs,
        },
        "events": events,
    }


def get_io_stats_attributes(prefix, io_stats):
    tables_used = []
    attrs = defaultdict(int)
    attrs[f"{prefix}.io_stats"] = io_stats["text"]
    for item in io_stats["data"]:
        table_name = item["table"]
        # Due to what looks like an upstream bug we sometimes get table names which look
        # like negative integers not real table names; we ignore these
        # https://github.com/opensafely-core/ehrql/issues/2494
        if re.match(r"\-?\d+", table_name):
            continue
        tables_used.append(table_name)
        if table_name.startswith("##results"):
            table_key = "results_tmp"
        elif table_name.startswith("#"):
            # Emiting individual temp table stats gets unwieldy so we aggregate them all
            # together
            table_key = "tmp"
        else:
            table_key = table_name
        for key in ("scans", "logical", "physical", "read_ahead"):
            value = int(item[key])
            attrs[f"{prefix}.table.{table_key}.{key}"] += value
            attrs[f"{prefix}.total_io.{key}"] += value
    attrs[f"{prefix}.tables_used"] = tables_used
    attrs[f"{prefix}.tables_used.count"] = len(tables_used)
    # Remove zero values to reduce noise
    attrs = {k: v for k, v in attrs.items() if v != 0}
    return attrs


def format_for_otel_fetch(group):
    prefix = "fetch"

    fetch_start = get_one(group["fetch_start"])
    batch_count = max((i["batch_seq"] for i in group["batch_start"]), default=0)
    retry_count = len(group["retry_query"])

    if group["fetch_complete"]:
        success = True
        end_timestamp = get_one(group["fetch_complete"])["timestamp"]
    elif group["next_record"] and group["next_record"]["type"] == "query_start":
        success = True
        end_timestamp = group["next_record"]["timestamp"]
    else:
        success = False
        end_timestamp = None

    if group["exception"]:
        success = False
        if end_timestamp is None:
            end_timestamp = group["exception"][0]["timestamp"]
        events = [format_for_otel_exception(exc) for exc in group["exception"]]
    else:
        events = []

    return {
        "name": "fetch",
        "start": fetch_start["timestamp"],
        "end": end_timestamp,
        "attributes": {
            f"{prefix}.success": success,
            f"{prefix}.batch_count": batch_count,
            f"{prefix}.retry_count": retry_count,
            "query.seq": fetch_start["query_seq"],
            "query.total_count": fetch_start["query_total_count"],
        },
        "events": events,
    }


def format_for_otel_exception(exception):
    return {
        "name": "exception",
        "timestamp": exception["timestamp"],
        "attributes": {
            "exception.type": exception["exception_type"],
            "exception.message": exception["message"],
            "exception.stacktrace": exception["stacktrace"],
        },
    }


def get_one(lst):
    assert len(lst) == 1, f"Expected one item in {lst}"
    return lst[0]


if __name__ == "__main__":
    main()
