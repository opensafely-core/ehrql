class EHRQLException(Exception):
    """Base exception for EHRQL errors of all sorts.

    This is not yet reliably used everywhere it should be.
    """


class Error(Exception):
    """
    Used to translate errors from the query model into something more
    ehrQL-appropriate
    """

    # Pretend this exception is defined in the top-level `ehrql` module: this allows us
    # to avoid leaking the internal `query_language` module into the error messages
    # without creating circular import problems.
    __module__ = "ehrql"


class DefinitionError(Exception):
    "Error in or with the user-supplied definition file"


class AssuranceTestError(Exception):
    pass


class FileValidationError(Exception):
    pass


class EHRQLPermissionError(Exception):
    pass


class MeasuresTimeout(Exception):
    pass


class DummyDataException(EHRQLException):
    """Base class for dummy data errors."""


class CannotGenerate(DummyDataException):
    """Raised when a population definition cannot be satisfied.

    This may be because it is logically impossible, or it may be
    logically possible but we were unable to do so.
    """


class ParameterError(EHRQLException):
    """Raised for errors in user-defined parameters"""
