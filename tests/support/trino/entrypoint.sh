#!/bin/bash

set -euo pipefail

if [ "$1" = '/usr/lib/trino/bin/run-trino' ]; then
  # If this is the container's first run, initialize the application
  # database
  if [ ! -f /tmp/app-initialized ]; then
    # Initialize the application database asynchronously in a
    # background process. This allows a) the trino process to be
    # the main process in the container, which allows graceful
    # shutdown and other goodies, and b) us to only start the trino
    # process once, as opposed to starting, stopping, then
    # starting it again.
    function initialize_app_database() {
        timeout=20
        limit="$((SECONDS + timeout))"

        # Note that the container has been initialized so future
        # starts won't wipe changes to the data
        touch /tmp/app-initialized
    }

    initialize_app_database &
  fi
fi

# The Docker library we're using hides stdout from us if the container exits with an error, so send everything to
# stderr.
exec "$@" 1>&2
