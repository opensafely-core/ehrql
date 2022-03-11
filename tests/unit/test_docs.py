import json

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
    generate_docs()

    with open("public_docs.json") as f:
        data = json.load(f)

    expected = {"DatabricksBackend", "GraphnetBackend", "TPPBackend"}
    output = {b["name"] for b in data["backends"]}
    assert expected <= output

    names = {contract["name"] for contract in data["contracts"]}
    assert "PatientDemographics" in names


def test_generate_docs_with_path(tmp_path):
    path = tmp_path / "test"
    path.mkdir()

    generate_docs(path)

    with open(path / "public_docs.json") as f:
        data = json.load(f)

    expected = {"DatabricksBackend", "GraphnetBackend", "TPPBackend"}
    output = {b["name"] for b in data["backends"]}
    assert expected <= output

    names = {contract["name"] for contract in data["contracts"]}
    assert "PatientDemographics" in names
