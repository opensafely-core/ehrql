import shutil
from pathlib import Path

import pytest

from ehrql.__main__ import main


FIXTURES_PATH = Path(__file__).parents[1] / "fixtures" / "good_definition_files"


@pytest.mark.skipif(
    shutil.which("dot") is None,
    reason="Graphing requires Graphviz library",
)
def test_graph_query(tmpdir):  # pragma: no cover
    output_file = tmpdir / "query.svg"
    main(
        [
            "graph-query",
            str(FIXTURES_PATH / "dataset_definition.py"),
            "--output",
            str(output_file),
        ]
    )
    assert output_file.exists()
