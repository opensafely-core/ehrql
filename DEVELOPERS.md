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
- smoke tests: tests that run the databuilder end to end in docker
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
a local spark db in a container, for reliability and speed.

Open source Spark and Databricks' Spark are very similar, and this provides
a good enough test basis for the SQL parts of a backend.

However, we still need to run tests against an actual Databricks instance, as
the way connections are made is different, and potentially more things down the
line.

Databricks is only only available in SaaS form. We can use the free Community
Edition version, but it is limited, slow, and not 100% reliable, so we do not
run it by default, it needs to be manually run. NHSD have given some of the
team (Simon, Seb, Dave) access to their Databricks sandbox, which is more
reliable. The NHSD DAE team negotiated these accounts for us, so you'll need
to go via them or other NHSD contact to get more.

We use some `just` commands and our helper script in `scripts/dbx` to ensure we
have a running Databricks cluster to run the tests against.


### Running locally against Databricks

First you need to set up your Databricks auth.


1. Register for a free account at https://community.cloud.databricks.com/. This
   same account is used whether accessing the NHSD Sandbox or not.

2. Log in to the databricks CLI tool (which is installed in the venv) with your
   credentials. For host, use either `https://community.cloud.databricks.com`
   for the Community Edition, or `https://drtl-theta.cloud.databricks.com/` for
   the NSHD sandbox.

   `databricks configure`

3. If using the NHSD sandbox, you will need to setup a cluster called
   `opensafely-test`, which you can do via the web UI via `Compute -> Create
   Cluster`, and just use all the default options.

4. Test it's working with: `databricks clusters list`. If that doesn't error,
   you are set up.


You should then be able to run tests against databricks with:

    just databricks-test [tests/backends/test_databricks.py]

Warning: running the full test suite takes a long time.

Note: This command will ensure there is an active Databricks cluster, and then
run the tests against it. When using Community Edition, it will create a cluster if needed
but if a cluster is alread up and running, it will use that. If it has
terminated (after 2 hours of inactivity), it will delete the old one and create
a new one.  When using the NSHD sandbox, it will only use manually pre-created
cluster called `opensafely-test`.

For more information about your Databricks cluster, you can use the dbx tool:

    just dbx

or

    ./scripts/dbx


### Running Databricks test in Github CI

You can manually run the tests in github by triggering the "Databricks CI"
action. By default it will just run the `tests/backends/test_databricks.py`,
but you can specify different arguments when you trigger it.

This CI uses simon.davy@thedatalab.org's Databricks account.

### Trouble Shooting


Sometimes Databricks filesystem gets left in an unclean state. You may see an error like:

`"Error running query: org.apache.spark.sql.AnalysisException: Cannot create table ('default.practice_registrations'). The associated location ('dbfs:/user/hive/warehouse/practice_registrations') is not empty but it's not a Delta table`

This means the Databricks filesystem needs cleaning up.

To do this:

    just dbx cleanup

If using Community Edition, you will need to follow the instructions the
command outputs to complete the cleanup process, as we cannot fully automate it
from the cli.
