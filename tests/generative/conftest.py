import sys

from .recording import recorder


__all__ = ["recorder"]


class BrokenDatabaseError(KeyboardInterrupt):
    def __init__(self, database):  # pragma: no cover
        self.database = database


def pytest_keyboard_interrupt(excinfo):  # pragma: no cover
    if isinstance(excinfo.value, BrokenDatabaseError):
        print(f"Unrecoverably broken {excinfo.value.database} database")
        sys.exit(6)
