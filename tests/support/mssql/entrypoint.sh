#!/bin/bash

set -euo pipefail

if [ "$1" = '/opt/mssql/bin/sqlservr' ]; then
  # If this is the container's first run, initialize the application
  # database
  if [ ! -f /tmp/app-initialized ]; then
    # Initialize the application database asynchronously in a
    # background process. This allows a) the SQL Server process to be
    # the main process in the container, which allows graceful
    # shutdown and other goodies, and b) us to only start the SQL
    # Server process once, as opposed to starting, stopping, then
    # starting it again.
    function initialize_app_database() {
        timeout=20
        limit="$((SECONDS + timeout))"

        # MSSQL doesn't apply the default collation specified in the
        # MSSQL_COLLATION environment variable immediately on startup. So we
        # need to wait for this to be applied before we create our application
        # databases, otherwise we have a race-condition. We check the collation
        # of "tempdb" as that's the system database whose collation affects us.
        until [[ "$(get_tempdb_collation)" == "$MSSQL_COLLATION" ]]; do
          sleep 1s
          if [[ "${SECONDS}" -gt "${limit}" ]]; then
            echo >&2 "Failed to connect to MSSQL and confirm collation setting after ${timeout} seconds"
            echo >&2 "Expected collation: $MSSQL_COLLATION"
            echo >&2 "Got: $(get_tempdb_collation)"
            exit 1
          fi
        done

        # Run the setup script to create the DB and the schema in the DB
        _sqlcmd -i /mssql/setup.sql

        # Note that the container has been initialized so future
        # starts won't wipe changes to the data
        touch /tmp/app-initialized
    }

    function get_tempdb_collation() {
      # We need to set NOCOUNT so we don't get a "Rows affected" count in the output
      _sqlcmd -Q "SET NOCOUNT ON; SELECT DATABASEPROPERTYEX('tempdb', 'Collation');"
    }

    function _sqlcmd() {
      # Extra arguments:
      #    -C : trust server certificate
      #    -b : exit with 1 on error rather than 0
      # -h -1 : no headers in output
      #    -W : trim trailing whitespace
      /opt/mssql-tools18/bin/sqlcmd \
        -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -d master \
        -C -b -h -1 -W \
        "$@"
    }

    initialize_app_database &
  fi
fi

# The Docker library we're using hides stdout from us if the container exits with an error, so send everything to
# stderr.
exec "$@" 1>&2
