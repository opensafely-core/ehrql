def records_to_html_table(records):
    rows = []
    headers_written = False

    for record in records:
        if not headers_written:
            headers = "".join([f"<th>{header}</th>" for header in record.keys()])
            headers_written = True
        row = "".join(f"<td>{val}</td>" for val in record.values())
        rows.append(f"<tr>{row}</tr>")
    rows = "".join([f"<tr>{row}</tr>" for row in rows])

    return f"<table><thead>{headers}</thead><tbody>{rows}</tbody></table>"


def records_to_ascii_table(records):
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


DISPLAY_RENDERERS = {
    "ascii": records_to_ascii_table,
    "html": records_to_html_table,
}
