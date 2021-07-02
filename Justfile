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

# run the unit tests only. Optional args are passed to pytest
test-unit ARGS="":
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    pytest -m "not integration" {{ ARGS }}

# run all tests including integration tests in slow mode. Optional args are passed to pytest
test-all ARGS="": build-cohort-extractor
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    MODE=slow pytest --cov=cohortextractor --cov=tests {{ ARGS }}

# run all tests including integration tests in fast mode (not suitable for GHAs). Optional args are passed to pytest
test-all-fast ARGS="":
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    MODE=fast pytest --cov=cohortextractor --cov=tests {{ ARGS }}

# alias for test_all. Optional args are passed to pytest
test:
    just test-all

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
