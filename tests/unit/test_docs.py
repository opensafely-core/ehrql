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
