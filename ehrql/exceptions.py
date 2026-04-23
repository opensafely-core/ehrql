class EHRQLException(Exception):
    """
    Base exception for EHRQL errors of all sorts.

    This is not yet reliably used everywhere it should be.
    """


class Error(EHRQLException):
    """
    Used to translate errors from the query model into something more
    ehrQL-appropriate
    """

    # Pretend this exception is defined in the top-level `ehrql` module: this allows us
    # to avoid leaking the internal `query_language` module into the error messages
    # without creating circular import problems.
    __module__ = "ehrql"


class EHRQLUserException(EHRQLException):
    "Base class for errors we display directly without a traceback"


class DefinitionError(EHRQLUserException):
    "Error in or with the user-supplied definition file"

    def __init__(self, message, exit_code=None):
        super().__init__(message)
        self.exit_code = exit_code


class AssuranceTestError(EHRQLUserException):
    "Assurance tests have failed"


class FileValidationError(EHRQLUserException):
    "Error reading a data file"


class EHRQLPermissionError(EHRQLUserException):
    "Insufficient permissions"


class MeasuresTimeout(EHRQLUserException):
    "Measure query progress is too slow"


class DummyDataException(EHRQLException):
    "Base class for dummy data errors"


class CannotGenerate(DummyDataException):
    """
    Raised when a population definition cannot be satisfied.

    This may be because it is logically impossible, or it may be
    logically possible but we were unable to do so.
    """


class ParameterError(EHRQLException):
    "Raised for errors in user-defined parameters"


def get_exit_code_for_exception(exc):
    """
    We use specific exit codes for specific errors because we can use these to indicate
    to the user why a job might have failed without them needing access to the logs
    """
    match exc:
        case DefinitionError():
            return 10
        case FileValidationError():
            return 11
        case EHRQLPermissionError():
            return 12
        case AssuranceTestError():
            return 13
        case MeasuresTimeout():
            return 14
        case _:
            return None
