import json
import sys

import pytest


@pytest.mark.skipif(
    not sys.platform.startswith("linux"),
    reason="Subprocess isolation only works on Linux",
)
def test_isolation_report(call_cli):
    captured = call_cli("isolation-report")
    assert json.loads(captured.out)
