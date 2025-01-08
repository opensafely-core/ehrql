import json
import sys

import pytest

from ehrql.__main__ import main


@pytest.mark.skipif(
    not sys.platform.startswith("linux"),
    reason="Subprocess isolation only works on Linux",
)
def test_isolation_report(capsys):
    main(["isolation-report"])
    assert json.loads(capsys.readouterr().out)
