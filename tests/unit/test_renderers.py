import textwrap

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
            "<table>"
            "<thead>"
            "<th>patient_id</th><th>i1</th><th>i2</th>"
            "</thead>"
            "<tbody>"
            "<tr><td>1</td><td>101</td><td>111</td></tr>"
            "<tr><td>2</td><td>201</td><td>211</td></tr>"
            "<tr><td>3</td><td>301</td><td>311</td></tr>"
            "<tr><td>4</td><td>401</td><td>411</td></tr>"
            "<tr><td>5</td><td>501</td><td>511</td></tr>"
            "</tbody>"
            "</table>"
        ),
    }
    rendered = DISPLAY_RENDERERS[render_format](TABLE.to_records()).strip()
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
            "<table>"
            "<thead>"
            "<th>patient_id</th><th>value</th>"
            "</thead>"
            "<tbody>"
            "<tr><td>1</td><td>101</td></tr>"
            "<tr><td>2</td><td>201</td></tr>"
            "</tbody>"
            "</table>"
        ),
    }

    c = PatientColumn.parse(
        """
        1 | 101
        2 | 201
        """
    )
    rendered = DISPLAY_RENDERERS[render_format](c.to_records()).strip()
    assert rendered == expected_output[render_format], rendered
