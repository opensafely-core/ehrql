from pathlib import Path


FIXTURES_PATH = Path(__file__).parents[1] / "fixtures" / "good_definition_files"


def test_assure(call_cli):
    captured = call_cli("assure", FIXTURES_PATH / "assurance.py")
    assert "All OK" in captured.out
