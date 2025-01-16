import typing


START_MARKER = "<!-- start debug output -->"
END_MARKER = "<!-- end debug output -->"


def headtail(sequence: typing.Sequence, head: int = 0, tail: int = 0):
    if head == tail == 0:
        return sequence, False, []

    # Check we have enough rows to truncate to head and tail
    if len(sequence) <= head + tail:
        return sequence, False, []

    head_rows = []
    tail_rows = []

    if head:
        head_rows = sequence[:head]

    if tail:
        tail_rows = sequence[-tail:]

    return head_rows, True, tail_rows


def records_to_html_table(records: list[dict], head: int = 0, tail: int = 0):
    rows = []
    headers = "".join([f"<th>{header}</th>" for header in records[0].keys()])
    head_rows, ellipsis, tail_rows = headtail(records, head, tail)

    def html_row(row):
        columns = "".join(f"<td>{v}</td>" for v in row.values())
        return f"<tr>{columns}</tr>"

    for row in head_rows:
        rows.append(html_row(row))

    if ellipsis:
        ellipsis_columns = "<td>&hellip;</td>" * len(records[0])
        rows.append(f"<tr>{ellipsis_columns}</tr>")

    for row in tail_rows:
        rows.append(html_row(row))

    html_rows = "".join(rows)

    return f"{START_MARKER}<table><thead><tr>{headers}</tr></thead><tbody>{html_rows}</tbody></table>{END_MARKER}"


def records_to_ascii_table(records: list[dict], head: int = 0, tail: int = 0):
    head_rows, ellipsis, tail_rows = headtail(records, head, tail)
    width = 17
    lines = []

    headers = records[0].keys()

    lines.append(" | ".join(name.ljust(width) for name in headers))
    lines.append("-+-".join("-" * width for _ in headers))

    for line in head_rows:
        lines.append(" | ".join(str(v).ljust(width) for v in line.values()))

    if ellipsis:
        ellipsis_row = " | ".join("...".ljust(width) for _ in headers)
        lines.append(ellipsis_row)

    for line in tail_rows:
        lines.append(" | ".join(str(v).ljust(width) for v in line.values()))

    return "\n".join(line.strip() for line in lines)


DISPLAY_RENDERERS = {
    "ascii": records_to_ascii_table,
    "html": records_to_html_table,
}
