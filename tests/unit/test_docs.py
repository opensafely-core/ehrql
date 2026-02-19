from ehrql.docs.__main__ import generate_docs, render
from ehrql.docs.render_includes.specs import render_specs


def test_generate_docs():
    data = generate_docs()

    expected = {"EMIS", "TPP"}
    output = {b["name"] for b in data["backends"]}
    assert expected <= output

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
                    assert leading_whitespace_count % 4 == 0


def test_render(tmp_path):
    assert not set(tmp_path.iterdir())
    render(generate_docs(), tmp_path)
    assert {pt.name for pt in tmp_path.iterdir()} == {
        "backends.md",
        "cli.md",
        "dummy_data_constraints.md",
        "language__codelists.md",
        "language__dataset.md",
        "language__date_arithmetic.md",
        "language__frames.md",
        "language__functions.md",
        "language__measures.md",
        "language__parameters.md",
        "language__permissions.md",
        "language__series.md",
        "schemas",
        "schemas.md",
        "specs.md",
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

```python
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

```python
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

```python
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
