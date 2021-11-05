import os

import pytest

import cohortextractor.main
from cohortextractor import codelist


def get_mode(name, values, default):
    key = f"{name}_MODE"
    mode = os.environ.get(key, default)
    if mode not in values:
        raise ValueError(
            f"Unknown {key} {mode}. Possible values are {','.join(values)}."
        )
    return mode


def extract(cohort, backend, database, **backend_kwargs):
    return list(
        cohortextractor.main.extract(
            cohort, backend(database.host_url(), **backend_kwargs)
        )
    )


def mark_xfail_in_playback_mode(wrapped):
    """
    The database playback framework cannot currently replay exceptions. In some
    cases we rely on exceptions from the database e.g. to check whether a table
    exists because we don't have sufficient permission to check in another way.
    Until we solve this problem we have to exempt tests which exercise this
    behaviour from being run in playback mode.

    Given that we run in record mode in CI the tests will still be enforced,
    just not when using the fast path locally.
    """
    mode = get_mode("RECORDING", ["record", "playback"], "playback")
    decorator = pytest.mark.xfail(
        mode == "playback", reason="playback framework cannot handle this test"
    )
    return decorator(wrapped)


class RecordingReporter:
    def __init__(self):
        self.msg = ""

    def __call__(self, msg):
        self.msg = msg


def null_reporter(msg):
    pass


def make_codelist(*codes, system="ctv3"):
    return codelist(codes, system=system)


def iter_flatten(iterable, iter_classes=(list, tuple)):
    """
    Iterate over `iterable` recursively flattening any lists or tuples
    encountered
    """
    for item in iterable:
        if isinstance(item, iter_classes):
            yield from iter_flatten(item, iter_classes)
        else:
            yield item
