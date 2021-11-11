# Notes for developers

## System requirements
- [just](https://github.com/casey/just)
- Docker
- recent version of Bash (see macOS notes)

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

Starting with version 4.0, Bash is licenced under GPLv3. Because of this, macOS still ships with version 3.2, which is incompatible with some scripts in this repository. We recommend using [homebrew](https://brew.sh/) to install a more recent version, and then ensure that it is on your `$PATH`.

```bash
brew install bash
```
