import pathlib

import pytest

import ehrql.dummy_data as dummy_data


PY_FILES = list(pathlib.Path(dummy_data.__file__).parent.glob("*.py"))


@pytest.mark.parametrize("file", PY_FILES, ids=[f.name for f in PY_FILES])
def test_dummy_data_does_not_refer_to_nextgen(file):
    with open(file) as i:
        source = i.read()

    namespace = {}
    exec(source, namespace, namespace)
    for name, value in namespace.items():
        if hasattr(value, "__module__") and value.__module__ is not None:
            assert "dummy_data_nextgen" not in value.__module__, name
