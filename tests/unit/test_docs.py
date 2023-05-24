from ehrql.docs import generate_docs, render
from ehrql.docs.common import reformat_docstring
from ehrql.docs.render_includes.backends import render_backend
from ehrql.docs.render_includes.contracts import render_contracts
from ehrql.docs.render_includes.specs import render_specs


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

    expected = {"TPPBackend"}
    output = {b["name"] for b in data["backends"]}
    assert expected <= output

    names = {contract["name"] for contract in data["contracts"]}
    assert "patients" in names

    # Find all series strings
    all_series = [
        paragraph["series"]
        for spec in data["specs"]
        for section in spec["sections"]
        for paragraph in section["paragraphs"]
    ]
    # Split the series string into its series and define_population components, if necessary
    # assert that each component string has no leading whitespace for the first and last lines,
    # and other lines have a multiple of 4 spaces
    for series in all_series:
        series_lines = series.split("\n")
        population_lines = []
        define_population_index = next(
            (
                i
                for i, line in enumerate(series_lines)
                if line.startswith("define_population")
            ),
            None,
        )
        if define_population_index:
            population_lines = series_lines[define_population_index:]
            series_lines = series_lines[:define_population_index]

        for lines_list in [series_lines, population_lines]:
            for i, line in enumerate(lines_list):
                if i in [0, len(lines_list) - 1]:
                    assert len(line.strip()) == len(line)
                else:
                    leading_whitespace_count = len(line) - len(line.strip())
                    assert leading_whitespace_count > 0
                    assert leading_whitespace_count % 4 == 0


def test_render(tmp_path):
    assert not set(tmp_path.iterdir())
    render(generate_docs(), tmp_path)
    assert {pt.name for pt in tmp_path.iterdir()} == {
        "specs.md",
        "contracts.md",
        "TPPBackend.md",
        "EMISBackend.md",
    }


def test_render_specs():
    specs = [
        {
            "id": "1",
            "title": "Filtering an event frame",
            "sections": [
                {
                    "id": "1.1",
                    "title": "Including rows",
                    "paragraphs": [
                        {
                            "id": "1.1.1",
                            "title": "Take with column",
                            "tables": {
                                "e": [
                                    ["", "i1", "b1"],
                                    ["1", "101", "T"],
                                    ["2", "201", "T"],
                                    ["2", "203", "F"],
                                    ["3", "302", "F"],
                                ]
                            },
                            "series": "e.where(e.b1).i1.sum_for_patient()",
                            "output": [["1", "203"], ["2", "201"], ["3", ""]],
                        }
                    ],
                }
            ],
        }
    ]

    expected = """## 1 Filtering an event frame


### 1.1 Including rows


#### 1.1.1 Take with column

This example makes use of an event-level table named `e` containing the following data:

| |i1|b1 |
| - | - | - |
| 1|101|T |
| 2|201|T |
| 2|203|F |
| 3|302|F |

```
e.where(e.b1).i1.sum_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|203 |
| 2|201 |
| 3| |
"""
    assert render_specs(specs) == expected


def test_render_specs_with_multiline_series():
    specs = [
        {
            "id": "1",
            "title": "Logical case expressions",
            "sections": [
                {
                    "id": "1.1",
                    "title": "Logical case expressions",
                    "paragraphs": [
                        {
                            "id": "1.1.1",
                            "title": "Case with expression",
                            "tables": {
                                "p": [
                                    ["patient", "i1"],
                                    ["1", "6"],
                                    ["2", "7"],
                                    ["3", "8"],
                                    ["4", "9"],
                                    ["5", ""],
                                ]
                            },
                            "series": "case(\n    when(p.i1 < 8).then(p.i1),\n    when(p.i1 > 8).then(100),\n)",
                            "output": [
                                ["1", "6"],
                                ["2", "7"],
                                ["3", ""],
                                ["4", "100"],
                                ["5", ""],
                            ],
                        }
                    ],
                }
            ],
        }
    ]

    expected = """## 1 Logical case expressions


### 1.1 Logical case expressions


#### 1.1.1 Case with expression

This example makes use of a patient-level table named `p` containing the following data:

| patient|i1 |
| - | - |
| 1|6 |
| 2|7 |
| 3|8 |
| 4|9 |
| 5| |

```
case(
    when(p.i1 < 8).then(p.i1),
    when(p.i1 > 8).then(100),
)
```
returns the following patient series:

| patient | value |
| - | - |
| 1|6 |
| 2|7 |
| 3| |
| 4|100 |
| 5| |
"""
    assert render_specs(specs) == expected


def test_specs_with_additional_text():
    specs = [
        {
            "id": "1",
            "title": "Filtering an event frame",
            "text": "Chapters may have additional descriptive text blocks",
            "sections": [
                {
                    "id": "1.1",
                    "title": "Including rows",
                    "text": "Additional text can also be added at a section level",
                    "paragraphs": [
                        {
                            "id": "1.1.1",
                            "title": "Take with column",
                            "text": "Further additional text can be provided for a paragraph",
                            "tables": {
                                "e": [
                                    ["", "i1", "b1"],
                                    ["1", "101", "T"],
                                    ["2", "201", "T"],
                                    ["2", "203", "F"],
                                    ["3", "302", "F"],
                                ]
                            },
                            "series": "e.where(e.b1).i1.sum_for_patient()",
                            "output": [["1", "203"], ["2", "201"], ["3", ""]],
                        }
                    ],
                }
            ],
        }
    ]
    assert render_specs(specs) == (
        """## 1 Filtering an event frame
Chapters may have additional descriptive text blocks


### 1.1 Including rows
Additional text can also be added at a section level


#### 1.1.1 Take with column
Further additional text can be provided for a paragraph

This example makes use of an event-level table named `e` containing the following data:

| |i1|b1 |
| - | - | - |
| 1|101|T |
| 2|201|T |
| 2|203|F |
| 3|302|F |

```
e.where(e.b1).i1.sum_for_patient()
```
returns the following patient series:

| patient | value |
| - | - |
| 1|203 |
| 2|201 |
| 3| |
"""
    )


def test_render_contracts():
    contracts = [
        {
            "name": "DummyClass",
            "hierarchy": ["some", "path"],
            "dotted_path": "dummy_module.DummyClass",
            "docstring": ["Dummy docstring"],
            "columns": [
                {
                    "name": "patient_id",
                    "description": "a column description",
                    "type": "PseudoPatientId",
                    "constraints": ["Must have a value", "Must be unique"],
                }
            ],
            "backend_support": [],
        },
        {
            "name": "DummyClass2",
            "hierarchy": ["some", "path"],
            "dotted_path": "dummy_module2.DummyClass2",
            "docstring": ["Dummy docstring2.", "", "Second line."],
            "columns": [],
            "backend_support": [],
        },
    ]
    expected = """## Some/Path/DummyClass

Dummy docstring

| Column name | Description | Type | Constraints |
| ----------- | ----------- | ---- | ----------- |
| patient_id | a column description | PseudoPatientId | Must have a value, must be unique. |




## Some/Path/DummyClass2

Dummy docstring2.

Second line.

| Column name | Description | Type | Constraints |
| ----------- | ----------- | ---- | ----------- |
"""
    assert render_contracts(contracts) == expected


def test_render_backend():
    backends = [
        {
            "name": "DummyBackend1",
            "contracts": ["Some/Path/DummyClass", "Some/Path/DummyClass2"],
        },
        {"name": "DummyBackend2", "contracts": ["some/path/DummyClass"]},
    ]
    assert render_backend(backends[0]) == (
        """Contracts implemented:

* [`Some/Path/DummyClass`](contracts-reference.md#somepathdummyclass)
* [`Some/Path/DummyClass2`](contracts-reference.md#somepathdummyclass2)
"""
    )

    assert render_backend(backends[1]) == (
        """Contracts implemented:

* [`some/path/DummyClass`](contracts-reference.md#somepathdummyclass)
"""
    )
