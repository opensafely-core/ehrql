import pprint
from contextlib import contextmanager
from pathlib import Path

import pymssql
from lib.util import get_mode


@contextmanager
def recording_for(identifier, is_passing):
    mode = get_mode("RECORDING", ["record", "playback"], "playback")
    if mode == "playback":
        recording = Recording.load(identifier)
        with _patch_pymssql(recording):
            yield recording.suspendable()
    if mode == "record":
        recording = Recording(identifier, "record")
        with _patch_pymssql(recording):
            yield recording.suspendable()
            if is_passing():
                assert recording.has_content(), "Refusing to dump a blank recording"
                recording.dump()


@contextmanager
def _patch_pymssql(recording):
    original_connect = pymssql.connect
    # noinspection PyPep8Naming
    original_Connection = pymssql.Connection
    # noinspection PyPep8Naming
    original_Cursor = pymssql.Cursor

    pymssql.connect = connect(recording, original_connect)

    # In pymssql these names are aliases for classes defined in an internal package. They are present to fulfill the
    # DBAPI contract, but they're never used directly. In practice all users of the DBAPI will go via the connect()
    # function, but we erase them just to be sure.
    del pymssql.Connection
    del pymssql.Cursor

    try:
        yield
    finally:
        pymssql.connect = original_connect
        pymssql.Connection = original_Connection
        pymssql.Cursor = original_Cursor


class Suspendable:
    """Wrapper around a recording to allow it to be temporarily suspended."""

    def __init__(self, recording):
        self._recording = recording

    @property
    def mode(self):
        return self._recording.mode

    @contextmanager
    def suspended(self):
        self._recording.suspend()
        try:
            yield
        finally:
            self._recording.resume()


class Recording:
    """
    A recording of a series of method calls. Can be persisted to disk and reloaded. Playback checks that the call is
    the same as during the recording and then returns the result. The recording is a single, linear stream across
    calls to all objections.
    """

    def __init__(self, test_name, mode, calls=None):
        self._test_name = test_name
        self._calls = calls or []
        self._seen_playback_error = False
        self._suspended = False
        self.mode = mode

    def record(self, target, method, args, kwargs, result):
        """Record a single method call."""
        if not self._suspended:
            self._calls.append(self._call(target, method, args, kwargs, result))

    def playback(self, target, method, args, kwargs):
        call = self._calls.pop(0)

        # Once there has been an error, SQLAlchemy will be making different calls to the happy path. We stop verifying
        # because there will inevitably be further failures which obscure the original problem.
        if not self._seen_playback_error:
            try:
                self._verify(call, target, method, args, kwargs)
            except RecordingStateException:
                self._seen_playback_error = True
                raise
        return self._call_result(call)

    def suspend(self):
        self._suspended = True

    def resume(self):
        self._suspended = False

    @staticmethod
    def _call(target, method, args, kwargs, result):
        call = target.__class__.__name__, method.__name__, args, kwargs, result
        assert pprint.isreadable(
            call
        )  # make sure we won't have deserialization problems later
        return call

    @staticmethod
    def _call_result(call):
        cls, method, args, kwargs, result = call
        return result

    @staticmethod
    def _verify(call, target, method, args, kwargs):
        call_class, call_method, call_args, call_kwargs, call_result = call

        class_name = target.__class__.__name__
        method_name = method.__name__
        if class_name != call_class or method_name != call_method:
            raise WrongCall(call_class, call_method, class_name, method_name)

        if args != call_args or kwargs != call_kwargs:
            raise WrongArgs(
                call_class, call_method, call_args, call_kwargs, args, kwargs
            )

    def has_content(self):
        return self._calls

    def dump(self):
        self._recording_root().mkdir(exist_ok=True)
        with open(self._recording_path(self._test_name), "w") as f:
            pprint.pp(self._calls, f)

    @staticmethod
    def load(test):
        path = Recording._recording_path(test)
        try:
            s = path.read_text()
        except FileNotFoundError as e:
            raise NoRecording(test) from e

        # We need this module in scope to deserialize dates
        import datetime  # noqa F401

        calls = eval(s)

        assert calls, f"Invalid recording {path} has no calls"
        return Recording(test_name=test, calls=calls, mode="playback")

    @staticmethod
    def _recording_path(test):
        return Recording._recording_root() / f"{test}.recording"

    @staticmethod
    def _recording_root():
        return Path(__file__).parent.parent / "recordings"

    def suspendable(self):
        return Suspendable(self)


class RecordingStateException(Exception):
    pass


class NoRecording(RecordingStateException):
    def __init__(self, test_name):
        super().__init__(
            f"No recording has been made for {test_name}. "
            f"You must run the tests with RECORDING_MODE=record."
        )


class WrongCall(RecordingStateException):
    def __init__(self, expected_class, expected_method, actual_class, actual_method):
        expected = f"{expected_class}.{expected_method}()"
        actual = f"{actual_class}.{actual_method}()"
        super().__init__(
            f"Sequence of DBAPI calls has changed.\n"
            f"Expected a call to {expected} but got one to {actual}.\n"
            f"You should run the tests with RECORDING_MODE=record and check the diffs."
        )


class WrongArgs(RecordingStateException):
    def __init__(
        self, cls, method, expected_args, expected_kwargs, actual_args, actual_kwargs
    ):
        expected = self._format(cls, method, expected_args, expected_kwargs)
        actual = self._format(cls, method, actual_args, actual_kwargs)
        super().__init__(
            f"Arguments to a DBAPI call have changed.\n"
            f"Expected a call to\n    {expected}\nbut got one to\n    {actual}\n"
            f"You should run the tests with RECORDING_MODE=record and check the diffs."
        )

    @staticmethod
    def _format(cls, method, args, kwargs):
        all_args = [repr(arg) for arg in args] + [
            f"{key}={value}" for key, value in kwargs.items()
        ]
        arg_string = ", ".join(all_args)
        return f"{cls}.{method}({arg_string})"


def record(method):
    """Decorator to allow record and playback of method calls."""

    def wrapper(target, *args, **kwargs):
        if target.recording.mode == "playback":
            return target.recording.playback(target, method, args, kwargs)
        if target.recording.mode == "record":
            result = method(target, *args, **kwargs)
            target.recording.record(target, method, args, kwargs, result)
            return result

    return wrapper


def connect(recording, original):
    """A record/playback wrapper for the DBAPI connect() entrypoint."""

    def wrapper(*args, **kwargs):
        if recording.mode == "playback":
            return Connection(None, recording)
        if recording.mode == "record":
            return Connection(original(*args, **kwargs), recording)

    return wrapper


class Connection:
    """A record/playback wrapper for the DBAPI Connection class."""

    def __init__(self, wrapped, recording):
        self._wrapped = wrapped
        self.recording = recording

    def cursor(self, *args, **kwargs):
        if self.recording.mode == "playback":
            return Cursor(None, self.recording)
        if self.recording.mode == "record":
            return Cursor(self._wrapped.cursor(*args, **kwargs), self.recording)

    @record
    def commit(self, *args, **kwargs):
        return self._wrapped.commit(*args, **kwargs)

    @record
    def rollback(self, *args, **kwargs):
        return self._wrapped.rollback(*args, **kwargs)

    @record
    def close(self, *args, **kwargs):
        return self._wrapped.close(*args, **kwargs)


class Cursor:
    """A record/playback wrapper for the DBAPI Cursor class."""

    def __init__(self, wrapped, recording):
        self._wrapped = wrapped
        self.recording = recording

    @record
    def execute(self, *args, **kwargs):
        return self._wrapped.execute(*args, **kwargs)

    @record
    def executemany(self, *args, **kwargs):
        return self._wrapped.executemany(*args, **kwargs)

    @property
    @record
    def description(self):
        return self._wrapped.description

    @property
    @record
    def rowcount(self):
        return self._wrapped.rowcount

    @record
    def fetchone(self):
        return self._wrapped.fetchone()

    @record
    def fetchall(self):
        return self._wrapped.fetchall()

    @record
    def close(self):
        self._wrapped.close()
