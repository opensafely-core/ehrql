import traceback
from pathlib import Path


# Note that if this file is moved, this will need to be updated.
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
# We want the trailing slash here so we can use this with `str.startswith()`
PACKAGE_ROOT_STR = str(PACKAGE_ROOT / "")


def get_trimmed_traceback(exc, filename):
    """Return only the relevant traceback lines from the supplied exception

    We only want to show lines from a user's own code, and not lines from our library
    code.
    """
    # Syntax errors are a special case because there's no first frame of user code
    # (because Python was unable to get as far as executing it)
    if isinstance(exc, SyntaxError) and exc.filename == filename:
        first_user_frame = None
    else:
        first_user_frame = extract_user_frames_from_traceback(
            exc.__traceback__, filename
        )
    return "".join(
        traceback.format_exception(type(exc), value=exc, tb=first_user_frame)
    )


def extract_user_frames_from_traceback(tb, filename):
    first_user_frame = next(
        next_tb for next_tb in walk_traceback(tb) if get_filename(next_tb) == filename
    )
    # By construction, this iterator can never be exhausted so we need to tell Coverage
    # not to moan at us about it
    last_user_frame = next(  # pragma: no branch
        next_tb
        for next_tb in walk_traceback(first_user_frame)
        if is_final_user_frame(next_tb)
    )
    # Truncate the traceback chain at the last user frame by NULLing the reference.
    # We're allowed to do this as `tb_next` is documented as writable, see:
    # https://docs.python.org/3/reference/datamodel.html#traceback-objects
    last_user_frame.tb_next = None
    return first_user_frame


def walk_traceback(tb):
    while tb is not None:
        yield tb
        tb = tb.tb_next


def get_filename(tb):
    # Your "Law of Demeter" has no power here
    return tb.tb_frame.f_code.co_filename


def is_final_user_frame(tb):
    # Is this the last frame of user code before we either get to the end of the
    # traceback or find ourselves inside ehrQL code?
    if tb.tb_next is None:
        return True
    else:
        return get_filename(tb.tb_next).startswith(PACKAGE_ROOT_STR)
