import pytest

from ehrql.utils.traceback_utils import get_trimmed_traceback, walk_traceback


# NOTE
#
# These tests exist purely to exercise some edge cases of the module and keep coverage
# happy. The actual behaviour of the module is covered in:
# tests/integeration/utils/test_traceback_utils.py


def test_walk_to_end_of_traceback():
    exc = exception_with_traceback()
    tb_list = list(walk_traceback(exc.__traceback__))
    assert len(tb_list) == 1


def test_get_trimmed_traceback_with_incorrect_filename():
    exc = exception_with_traceback()
    with pytest.raises(StopIteration):
        get_trimmed_traceback(exc, "no_such_file")


def exception_with_traceback():
    try:
        raise ValueError()
    except ValueError as exc:
        return exc
