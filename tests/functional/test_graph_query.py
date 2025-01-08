import shutil
from pathlib import Path

import pytest


FIXTURES_PATH = Path(__file__).parents[1] / "fixtures" / "good_definition_files"


@pytest.mark.skipif(
    shutil.which("dot") is None,
    reason="Graphing requires Graphviz library",
)
def test_graph_query(call_cli, tmpdir):  # pragma: no cover
    output_file = tmpdir / "query.svg"
    call_cli(
        "graph-query",
        FIXTURES_PATH / "dataset_definition.py",
        "--output",
        output_file,
    )
    assert output_file.exists()
