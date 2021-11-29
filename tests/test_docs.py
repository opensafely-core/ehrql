import json

from cohortextractor2.docs import _reformat_docstring, generate_docs


def test_reformat_docstring():
    docstring = """
    First line.

    Second line.
    """

    output = _reformat_docstring(docstring)

    expected = [
        "First line.",
        "",
        "Second line.",
    ]
    assert output == expected


def test_generate_docs():
    generate_docs()

    with open("backend_docs.json") as f:
        data = json.load(f)

    expected = {"DatabricksBackend", "GraphnetBackend", "TPPBackend"}
    output = {b["name"] for b in data["backends"]}
    assert expected <= output

    assert data["contracts"][0]["name"] == "ClinicalEvents"
    assert data["contracts"][1]["name"] == "PatientDemographics"
    assert data["contracts"][2]["name"] == "PracticeRegistrations"
