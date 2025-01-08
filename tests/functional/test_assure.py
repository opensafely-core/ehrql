from pathlib import Path

from ehrql.__main__ import main


FIXTURES_PATH = Path(__file__).parents[1] / "fixtures" / "good_definition_files"


def test_assure(capsys):
    main(["assure", str(FIXTURES_PATH / "assurance.py")])
    out, _ = capsys.readouterr()
    assert "All OK" in out
