class EHRQLException(Exception):
    """Base exception for EHRQL errors of all sorts.

    This is not yet reliably used everywhere it should be.
    """


class DummyDataException(EHRQLException):
    """Base class for dummy data errors."""


class CannotGenerate(DummyDataException):
    """Raised when a population definition cannot be satisfied.

    This may be because it is logically impossible, or it may be
    logically possible but we were unable to do so.
    """
