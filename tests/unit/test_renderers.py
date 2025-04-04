import textwrap
from itertools import product

import pytest

from ehrql.query_engines.in_memory_database import (
    PatientColumn,
    PatientTable,
)
from ehrql.renderers import DISPLAY_RENDERERS


TABLE = PatientTable.parse(
    """
      |  i1 |  i2
    --+-----+-----
    1 | 101 | 111
    2 | 201 | 211
    3 | 301 | 311
    4 | 401 | 411
    5 | 501 | 511
    """
)


@pytest.mark.parametrize("render_format", ["ascii", "html"])
def test_render_table(render_format):
    expected_output = {
        "ascii": textwrap.dedent(
            """
            patient_id        | i1                | i2
            ------------------+-------------------+------------------
            1                 | 101               | 111
            2                 | 201               | 211
            3                 | 301               | 311
            4                 | 401               | 411
            5                 | 501               | 511
            """
        ).strip(),
        "html": (
            "<!-- start debug output -->"
            "<table>"
            "<thead>"
            "<tr><th>patient_id</th><th>i1</th><th>i2</th></tr>"
            "</thead>"
            "<tbody>"
            "<tr><td>1</td><td>101</td><td>111</td></tr>"
            "<tr><td>2</td><td>201</td><td>211</td></tr>"
            "<tr><td>3</td><td>301</td><td>311</td></tr>"
            "<tr><td>4</td><td>401</td><td>411</td></tr>"
            "<tr><td>5</td><td>501</td><td>511</td></tr>"
            "</tbody>"
            "</table>"
            "<!-- end debug output -->"
        ),
    }
    rendered = DISPLAY_RENDERERS[render_format](list(TABLE.to_records())).strip()
    assert rendered == expected_output[render_format], rendered


@pytest.mark.parametrize("render_format", ["ascii", "html"])
def test_render_column(render_format):
    expected_output = expected_output = {
        "ascii": textwrap.dedent(
            """
            patient_id        | value
            ------------------+------------------
            1                 | 101
            2                 | 201
            """
        ).strip(),
        "html": (
            "<!-- start debug output -->"
            "<table>"
            "<thead>"
            "<tr><th>patient_id</th><th>value</th></tr>"
            "</thead>"
            "<tbody>"
            "<tr><td>1</td><td>101</td></tr>"
            "<tr><td>2</td><td>201</td></tr>"
            "</tbody>"
            "</table>"
            "<!-- end debug output -->"
        ),
    }

    c = PatientColumn.parse(
        """
        1 | 101
        2 | 201
        """
    )
    rendered = DISPLAY_RENDERERS[render_format](list(c.to_records())).strip()
    assert rendered == expected_output[render_format], rendered


@pytest.mark.parametrize("render_format", ["ascii", "html"])
def test_render_table_head(render_format):
    expected_output = {
        "ascii": textwrap.dedent(
            """
            patient_id        | i1                | i2
            ------------------+-------------------+------------------
            1                 | 101               | 111
            2                 | 201               | 211
            ...               | ...               | ...
            """
        ).strip(),
        "html": (
            "<!-- start debug output -->"
            "<table>"
            "<thead>"
            "<tr><th>patient_id</th><th>i1</th><th>i2</th></tr>"
            "</thead>"
            "<tbody>"
            "<tr><td>1</td><td>101</td><td>111</td></tr>"
            "<tr><td>2</td><td>201</td><td>211</td></tr>"
            "<tr><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td></tr>"
            "</tbody>"
            "</table>"
            "<!-- end debug output -->"
        ),
    }

    truncated = DISPLAY_RENDERERS[render_format](list(TABLE.to_records()), head=2)
    assert truncated == expected_output[render_format], truncated


@pytest.mark.parametrize("render_format", ["ascii", "html"])
def test_render_table_tail(render_format):
    expected_output = {
        "ascii": textwrap.dedent(
            """
            patient_id        | i1                | i2
            ------------------+-------------------+------------------
            ...               | ...               | ...
            4                 | 401               | 411
            5                 | 501               | 511
            """
        ).strip(),
        "html": (
            "<!-- start debug output -->"
            "<table>"
            "<thead>"
            "<tr><th>patient_id</th><th>i1</th><th>i2</th></tr>"
            "</thead>"
            "<tbody>"
            "<tr><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td></tr>"
            "<tr><td>4</td><td>401</td><td>411</td></tr>"
            "<tr><td>5</td><td>501</td><td>511</td></tr>"
            "</tbody>"
            "</table>"
            "<!-- end debug output -->"
        ),
    }

    truncated = DISPLAY_RENDERERS[render_format](list(TABLE.to_records()), tail=2)
    assert truncated == expected_output[render_format], truncated


@pytest.mark.parametrize("render_format", ["ascii", "html"])
def test_render_table_head_and_tail(render_format):
    expected_output = {
        "ascii": textwrap.dedent(
            """
            patient_id        | i1                | i2
            ------------------+-------------------+------------------
            1                 | 101               | 111
            2                 | 201               | 211
            ...               | ...               | ...
            4                 | 401               | 411
            5                 | 501               | 511
            """
        ).strip(),
        "html": (
            "<!-- start debug output -->"
            "<table>"
            "<thead>"
            "<tr><th>patient_id</th><th>i1</th><th>i2</th></tr>"
            "</thead>"
            "<tbody>"
            "<tr><td>1</td><td>101</td><td>111</td></tr>"
            "<tr><td>2</td><td>201</td><td>211</td></tr>"
            "<tr><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td></tr>"
            "<tr><td>4</td><td>401</td><td>411</td></tr>"
            "<tr><td>5</td><td>501</td><td>511</td></tr>"
            "</tbody>"
            "</table>"
            "<!-- end debug output -->"
        ),
    }

    truncated = DISPLAY_RENDERERS[render_format](
        list(TABLE.to_records()), head=2, tail=2
    )
    assert truncated == expected_output[render_format], truncated


@pytest.mark.parametrize(
    "render_format,head_tail",
    list(product(["ascii"], [(0, 0), (2, 3), (5, 0), (0, 6), (3, 3)])),
)
def test_render_table_bad_head_tail(render_format, head_tail):
    expected_output = {
        "ascii": textwrap.dedent(
            """
            patient_id        | i1                | i2
            ------------------+-------------------+------------------
            1                 | 101               | 111
            2                 | 201               | 211
            3                 | 301               | 311
            4                 | 401               | 411
            5                 | 501               | 511
            """
        ).strip(),
        "html": (
            "<!-- start debug output -->"
            "<table>"
            "<thead>"
            "<tr><th>patient_id</th><th>i1</th><th>i2</th></tr>"
            "</thead>"
            "<tbody>"
            "<tr><td>1</td><td>101</td><td>111</td></tr>"
            "<tr><td>2</td><td>201</td><td>211</td></tr>"
            "<tr><td>3</td><td>301</td><td>311</td></tr>"
            "<tr><td>4</td><td>401</td><td>411</td></tr>"
            "<tr><td>5</td><td>501</td><td>511</td></tr>"
            "</tbody>"
            "</table>"
            "<!-- end debug output -->"
        ),
    }
    head, tail = head_tail
    truncated = DISPLAY_RENDERERS[render_format](
        list(TABLE.to_records()), head=head, tail=tail
    )
    assert truncated == expected_output[render_format], (truncated, head, tail)
