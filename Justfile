# list available commands
default:
    @just --list

# build the cohort-extractor docker image
build-cohort-extractor:
    docker build . -t cohort-extractor-v2

# tear down the persistent cohort-extractor-mssql docker container and network
remove-persistent-database:
    docker rm --force cohort-extractor-mssql
    docker network rm cohort-extractor-network

# Full set of tests run by CI
test: test-assert-recordings-up-to-date test-all

# run the unit tests only. Optional args are passed to pytest
test-unit ARGS="":
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    pytest -m "not integration and not smoke" {{ ARGS }}

# run the integration tests only. Optional args are passed to pytest
test-integration ARGS="":
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    DATABASE_MODE="${DATABASE_MODE:-ephemeral}" RECORDING_MODE="${RECORDING_MODE:-playback}" pytest -m integration {{ ARGS }}

# run the integration tests only against a persistent database. Optional args are passed to pytest
test-integration-fast ARGS="":
    DATABASE_MODE=persistent just test-integration '{{ ARGS }}'

# run the smoke tests only. Optional args are passed to pytest
test-smoke ARGS="":
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    DATABASE_MODE="${DATABASE_MODE:-ephemeral}" pytest -m smoke {{ ARGS }}

# run the smoke tests only against a persistent database. Optional args are passed to pytest
test-smoke-fast ARGS="":
    DATABASE_MODE=persistent just test-smoke '{{ ARGS }}'

# run all tests including integration and smoke tests. Optional args are passed to pytest
test-all ARGS="": build-cohort-extractor
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    DATABASE_MODE="${DATABASE_MODE:-ephemeral}" RECORDING_MODE="${RECORDING_MODE:-playback}" pytest --cov=cohortextractor --cov=tests {{ ARGS }}

# run all tests including integration and smoke tests against a persistent database. Optional args are passed to pytest
test-all-fast ARGS="":
    DATABASE_MODE=persistent just test-all '{{ ARGS }}'

# run all tests in record mode with ephemeral databases. Optional args are passed to pytest
test-record ARGS="":
    RECORDING_MODE=record just test-integration '{{ ARGS }}'

# run all tests in record mode with a persistent database (note: may produce unexpected recording changes relating to clearing out the database contents). Optional args are passed to pytest
test-record-fast ARGS="":
    RECORDING_MODE=record just test-integration-fast '{{ ARGS }}'

# check that the recordings are up-to-date
test-assert-recordings-up-to-date:
    #!/usr/bin/env bash
    set -euo pipefail

    rm tests/recordings/*.recording
    just test-record
    git update-index -q --really-refresh # avoid false positives due to last modification time changing
    if ! git diff-index --quiet HEAD -- tests/recordings; then
        git status -- tests/recordings
        echo >&2 "ERROR: Recordings are not up-to-date"
        exit 1
    fi

# runs the format (black), sort (isort) and lint (flake8) check but does not change any files
check:
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    black --check .
    isort --check-only --diff .
    flake8

# fix formatting and import sort ordering
fix:
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    black .
    isort .

# compile and update python dependencies.  <target> specifies an environment to update (dev/prod).
update target="prod":
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    echo "Updating and installing requirements"
    pip-compile --generate-hashes --output-file=requirements.{{ target }}.txt requirements.{{ target }}.in
    pip install -r requirements.{{ target }}.txt
