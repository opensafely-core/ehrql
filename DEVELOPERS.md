# Notes for developers

## System requirements
- [just](https://github.com/casey/just)
- Docker
- recent version of Bash (see macOS notes)

## Local development environment
The `just` command provides a list of available recipes:
```
just list
```

Running any of the test/check/fix `just` commands will setup a local environment and
install dependencies.


## Test setup

The test suite includes:
- smoke tests: tests that run the cohortextractor end to end in docker
- integration tests: tests that require a database
- unit tests that don't require a database

We run the database for the integration and smoke tests in a Docker container. Each run of the tests starts the
database if it's not already running _and then leaves it running_ at the end to speed up future runs. (Each test cleans
out the schema to avoid pollution.)

### Running the tests:

To run all tests, as they're run in CI:
`just test`

To run just the integration tests
```
just test-integration
```

To run just the smoke tests
```
just test-smoke
```

To run just the unit (non-smoke and non-integration) tests:
```
just test-unit
```

Additional arguments can be passed to any test commands, e.g.
```
just test-integration tests/acceptance
```

To pass multiple args, wrap in quotes, e.g.:
```
just test-integration '-s tests/acceptance'
```

To remove the persistent database container:
```
just remove-persistent-database
```

### Displaying SQL queries

Set the environment variable `LOG_SQL=1` (or anything non-empty) to get
all SQL queries logged to the console.

## macOS / Bash

Starting with version 4.0, Bash is licenced under GPLv3. Because of this, macOS still ships with version 3.2, which is incompatible with some scripts in this repository. We recommend using [homebrew](https://brew.sh/) to install a more recent version, ensure that the new version is on your `$PATH`, and restart your Terminal/shell session if necessary.

```bash
brew install bash
```


## Running tests against Databricks

The test suite for Databricks/Spark backend by default runs tests against
a local spark db in a container, for reliablility and speed.

Open source Spark and Databricks' Spark are very similar, and this provides
a good enough tests for the SQL parts of a backend.

However, we still need to run tests against an actual Databricks instance, as
the way the initial connection is made is different, and potentially other
things also. We can run the test manually, using a helper script in
`scripts/dbx` to manage our Databricks instance.


### Running locally against Databricks

First you need to set up your Databricks auth.

1. Register for a free account at https://community.cloud.databricks.com/

2. Log in to the databricks CLI tool (which is installed in the venv):

    databricks configure --host https://community.cloud.databricks.com

3. Test it's working with: `databricks clusters list`. If that doesn't error,
   you are set up.


You should then be able to run tests against databricks with:

    just databricks-test [tests/backends/test_databricks.py]

Warning: running the full test suite takes a long time.

Note: This command will ensure there is an active Databricks cluster, and then
run the tests against it.  Cluster creation is idempotent - if a cluster is
alread up and running, it will use that. If it has terminated (after 2 hours of
inactivity), it will delete the old one and create a new one.

For more information about your Databricks cluster, you can use the dbx tool:

    just dbx

    unset DATABRICKS_URL

5. Run the tests you want to run, e.g.

    just test tests/backend/test_databricks.py
