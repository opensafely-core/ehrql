from ehrql.utils.itertools_utils import eager_iterator


def generate_html(results, column_specs):
    results = eager_iterator(results)

    headers = "".join([f"<th>{column_name}</th>" for column_name in column_specs])
    rows = []
    for result in results:
        values = "".join([f"<td>{value}</td>" for value in result])
        rows.append(f"<tr>{values}</tr>")
    rows = "".join(rows)

    return f"""
    <html>
    <head>
    <style>
        table, th, td {{
            border: 1px solid;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
    </style>
    </head>
    <body>
        <table>
        <thead>{headers}</thead>
        <tbody>{rows}</tbody>
        </table>
    </body>
    </html>
    """
