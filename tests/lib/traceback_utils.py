import traceback


def get_traceback(exc_info):
    return "\n".join(traceback.format_exception(exc_info.value))


def assert_traceback_context_suppressed(exc_info):
    # In general, when we catch a low-level error and raise a user-facing one we don't
    # want the original error displayed in the traceback. It's our job to make sure that
    # the user-facing error contains enough information to debug the problem; including
    # the low level stuff just makes the traceback more intimidating and harder to read.
    assert (
        "During handling of the above exception, another exception occurred"
        not in get_traceback(exc_info)
    ), "Exception context not suppressed"
