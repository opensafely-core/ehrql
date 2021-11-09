# Notes for developers

## System requirements
- [just](https://github.com/casey/just)
- Docker

## Local development environment
Running any of the test/check/fix `just` commands will setup a local environment and
install dependencies.

To update dependencies:
```
just update dev  # update dev dependencies
just update prod  # update prod dependencies
```

To run checks (flake8, black, isort):
```
just check
```

To run black and isort and apply changes:
```
just fix
```

## Test setup

The test suite include:
- smoke tests: tests that run the cohortextractor end to end in docker
- integration tests: tests that require a database
- unit tests that don't require a database

In addition, the test suite can run with one of two database modes:
- ephemeral: the test database is set up and run in a docker container just for
  the duration of the test run
- persistent: uses (and starts up, if it isn't already running) a persistent database

and in one of two recording modes:
- recording: uses a real database and records the SQL generated from each test (stored in tests/recordings)
- playback: just checks generated SQL against the existing recordings

### Running the tests:

To run all tests, as they're run in CI:
`just test`

This runs all tests in recording mode and verifies that no recordings have changed.  It
then runs all tests in playback mode.

To run all tests in playback mode:
```
just test-all
```

To run all tests in recording mode:
```
just test-record  # ephemeral database
just test-record-fast  # persistent database
```

To run just the integration tests
```
just test-integration  # ephemeral database
just test-integration-fast  # persistent database
```

To run just the smoke tests
```
just test-smoke  # ephemeral database
just test-smoke-fast`  # persistent database
```

To run just the unit (non-smoke and non-integration) tests:
```
just test-unit
```

Additional arguments can be passed to any test commands, e.g.
```
just test-record tests/acceptance
```

To pass multiple args, wrap in quotes, e.g.:
```
just test-record '-s tests/acceptance'
```

To remove the persistent database:
```
just remove-persistent-database
```

### Displaying SQL queries

Set the environment variable `LOG_SQL=1` (or anything non-empty) to get
all SQL queries logged to the console.
