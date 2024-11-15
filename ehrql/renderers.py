import re


def records_to_html_table(records: list[dict]):
    rows = []
    headers_written = False

    for record in records:
        if not headers_written:
            headers = "".join([f"<th>{header}</th>" for header in record.keys()])
            headers_written = True
        row = "".join(f"<td>{val}</td>" for val in record.values())
        rows.append(f"<tr>{row}</tr>")
    rows = "".join(rows)

    return f"<table><thead>{headers}</thead><tbody>{rows}</tbody></table>"


def records_to_ascii_table(records: list[dict]):
    width = 17
    lines = []
    headers_written = False
    for record in records:
        if not headers_written:
            lines.append(" | ".join(name.ljust(width) for name in record.keys()))
            lines.append("-+-".join("-" * width for _ in record.keys()))
            headers_written = True
        lines.append(" | ".join(str(value).ljust(width) for value in record.values()))
    return "\n".join(line.strip() for line in lines) + "\n"


def _truncate_html_table(table_repr: str, head: int | None, tail: int | None):
    """
    Truncate an html table string to the first/last N rows, with a row of ...
    values to indicate where it's been truncated
    """
    regex = re.compile(
        r"(?P<start>^<table>.*<tbody>)(?P<rows><tr>.*<\/tr>)(?P<end><\/tbody>.*<\/table>)"
    )
    match = regex.match(table_repr)
    if match is None:
        # if we can't parse the table, return None and let the fallback handle it
        return

    start = match.group("start")
    rows = match.group("rows")
    end = match.group("end")

    # Check we have enough rows to truncate to head and tail
    if rows.count("<tr>") <= ((head or 0) + (tail or 0)):
        return table_repr

    # split row on <tr> tokens, remove any empty strings (this will lose the first <tr> of
    # each row, but we'll add it in again later)
    rows = [row for row in rows.split("<tr>") if row]
    # compose an "ellipsis row" to mark the place of truncated rows
    td_count = rows[0].count("<td>")
    ellipsis_row = f"{'<td>...</td>'*td_count}</tr>"

    # Build the list of rows we need to include, with ellipsis rows where necessary
    truncated_rows = []

    head_rows = rows[:head] if head is not None else [ellipsis_row]
    truncated_rows.extend(head_rows)

    if head is not None and tail is not None:
        truncated_rows.append(ellipsis_row)

    tail_rows = rows[-tail:] if tail is not None else [ellipsis_row]
    truncated_rows.extend(tail_rows)

    # re-join the truncated rows with <tr>
    truncated_rows = "<tr>" + "<tr>".join(truncated_rows)
    return start + truncated_rows + end


def _truncate_lines(
    table_repr: str, headers: int = 0, head: int | None = None, tail: int | None = None
):
    table_rows = [row for row in table_repr.split("\n") if row]

    # Check we have enough rows to truncate to head and tail
    if len(table_rows) <= (headers + (head or 0) + (tail or 0)):
        return table_repr

    # compose an "ellipsis row" to mark the place of truncated rows
    cell_count = table_rows[0].count("|") + 1
    ellipsis_row = " | ".join("...".ljust(17) for i in range(cell_count)).strip()

    # Build the list of rows we need to include, with ellipsis rows where necessary
    truncated_rows = table_rows[:headers]

    head_rows = (
        table_rows[headers : headers + head] if head is not None else [ellipsis_row]
    )
    truncated_rows.extend(head_rows)

    if head is not None and tail is not None:
        truncated_rows.append(ellipsis_row)

    tail_rows = table_rows[-tail:] if tail is not None else [ellipsis_row]
    truncated_rows.extend(tail_rows)

    return "\n".join(truncated_rows)


def truncate_table(table_repr: str, head: int | None, tail: int | None):
    """
    Take a table repr (ascii or html format) and truncate it to show only the
    first and/or last N rows.
    """
    if head is None and tail is None:
        return table_repr

    truncated_repr = None

    if "<table>" in table_repr:
        truncated_repr = _truncate_html_table(table_repr, head=head, tail=tail)
    elif "---+---" in table_repr:
        truncated_repr = _truncate_lines(table_repr, headers=2, head=head, tail=tail)

    # if we didn't detect either an ascii or html table, or the html regex
    # didn't match as expected, fall back to a simple truncation of lines using
    # line breaks.
    if truncated_repr is None:
        truncated_repr = _truncate_lines(table_repr, head=head, tail=tail)
    return truncated_repr


DISPLAY_RENDERERS = {
    "ascii": records_to_ascii_table,
    "html": records_to_html_table,
}
