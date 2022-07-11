from databuilder.docs import generate_docs
from databuilder.docs.common import reformat_docstring


def test_reformat_docstring():
    docstring = """
    First line.

    Second line.
    """

    output = reformat_docstring(docstring)

    expected = [
        "First line.",
        "",
        "Second line.",
    ]
    assert output == expected


def test_generate_docs():
    data = generate_docs()

    expected = {"DatabricksBackend", "GraphnetBackend", "TPPBackend"}
    output = {b["name"] for b in data["backends"]}
    assert expected <= output

    names = {contract["name"] for contract in data["contracts"]}
    assert "PatientDemographics" in names

    # Find all series strings
    all_series = [
        paragraph["series"]
        for spec in data["specs"]
        for section in spec["sections"]
        for paragraph in section["paragraphs"]
    ]
    # assert that a series string has no leading whitespace for the first and last lines, and
    # other lines have a multiple of 4 spaces
    for series in all_series:
        lines = series.split("\n")
        for i, line in enumerate(lines):
            if i in [0, len(lines) - 1]:
                assert len(line.strip()) == len(line)
            else:
                leading_whitespace_count = len(line) - len(line.strip())
                assert leading_whitespace_count > 0
                assert leading_whitespace_count % 4 == 0
