"""
TPP Specific maintenance mode query.

A BuildProgress table with the following columns:

    Event (VARCHAR) - A description of the event
    BuildStart (DATETIME) - When the overall build started
    EventStart (DATETIME) - When the event started
    EventEnd (DATETIME) - When the event ended
    Duration (INT) - The duration in minutes

TPP will insert events for:
- The overall build (Event = 'OpenSAFELY') - This will span the other events
- Swapping the main tables (Event = 'Swap Tables')
- Building the CodedEvent_SNOMED table (Event = 'CodedEvent_SNOMED')

Events from the same overall build will have the same BuildStart value
A row will be inserted when the event starts with EventEnd = 31 Dec 9999
That row will be updated when the event ends to set EventEnd and Duration
So the trigger to kill currently running jobs and prevent more from
starting will be the presence of a 'Swap Tables' row with a Start but
no End.

The trigger to exit maintenance mode is when the final OpenSAFELY event
finishes.

DB builds occur every 4 weeks. In the past they were weekly, and occassionally
the build would be slow (usually due to intensive concurrent DB queries),
and the previous week's build did not complete before the next build started. In
this case we ended up with two ongoing builds, and in order to determine DB status
we needed to check for ongoing SwapTables or CodedEvent_SNOMED events since the start
of the earlier build. We retain this check even though the builds are now less
frequent and this is unlikely to happen.

The presence of two ongoing builds is a flag for something that we want to alert on,
so we also return the build count.
"""

import sqlalchemy

from ehrql.__main__ import add_dsn_argument


HELP = "Check whether the TPP database is currently in maintenance mode"


def add_arguments(parser, environ):
    add_dsn_argument(parser, environ)


def run(*, backend_class, dsn, environ, user_args):
    backend = backend_class(environ)
    query_engine = backend.get_query_engine(dsn)

    with query_engine.engine.connect() as connection:
        maintenance_mode, build_count = get_mode_and_build_count(connection, environ)
        # Print output so a wrapping `docker run` (i.e. a RAP agent job) can read from
        # the container's stdout and report the results to the RAP controller.
        if maintenance_mode:
            print(f"db-maintenance;{build_count}")
        else:
            print(f"none;{build_count}")


def get_mode_and_build_count(connection, environ):

    # Select the TWO most recently started overall OpenSAFELY build events
    results = connection.execute(
        sqlalchemy.text("""
        SELECT TOP 2 EventStart, EventEnd
        FROM BuildProgress
        WHERE Event = 'OpenSAFELY'
        ORDER BY EventStart DESC
        """)
    )
    latest_rebuilds = list(results)
    if not latest_rebuilds:
        # No events at all, we can't be in maintenance mode
        return False, 0

    # Of the two most recently started builds, identify those that are ongoing (i.e.
    # those with an end date of 9999-12-31)
    _, most_recent_end = latest_rebuilds[0]
    if most_recent_end.year < 9999:
        # The most recent build is complete, so we're not in maintenance mode, and any
        # previous build is a historical one which we can ignore
        return False, 0

    ongoing_builds = [rebuild for rebuild in latest_rebuilds if rebuild[1].year == 9999]
    build_count = len(ongoing_builds)

    # Check for events starting on or after the start of the earliest ongoing build
    earliest_build_start_date = min(ongoing_builds)[0]
    result = connection.execute(
        sqlalchemy.text(
            "SELECT Event, EventEnd FROM BuildProgress WHERE EventStart >= :start_date"
        ),
        {"start_date": earliest_build_start_date},
    )
    current_events = {row[0] for row in result}

    # Env var allows quick change of start event logic if needed
    start_events = environ.get(
        "TPP_MAINTENANCE_START_EVENT", "Swap Tables,CodedEvent_SNOMED"
    ).split(",")

    # We start maintenance mode as soon as we see any of the "trigger" events
    # and then don't exit until the entire build is finished
    in_maintenance_mode = bool(current_events.intersection(start_events))

    if not in_maintenance_mode:
        # According to the events, we're not in maintenance mode. As a final check,
        # make sure that the CodedEvent_SNOMED table really is available.
        try:
            connection.execute(
                sqlalchemy.text("SELECT TOP 1 CodedEvent_ID FROM CodedEvent_SNOMED")
            )
        except sqlalchemy.exc.ProgrammingError:
            in_maintenance_mode = True

    return in_maintenance_mode, build_count
