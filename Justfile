# list available commands
default:
    @just --list

# build the cohort-extractor docker image
build-cohort-extractor:
    #!/usr/bin/env bash
    set -euo pipefail

    [[ -v CI ]] && echo "::group::Build cohort-extractor (click to view)" || echo "Build cohort-extractor"
    docker build . -t cohort-extractor-v2
    [[ -v CI ]] && echo "::endgroup::" || echo ""

# tear down the persistent cohort-extractor-mssql docker container and network
remove-persistent-database:
    docker rm --force cohort-extractor-mssql
    docker network rm cohort-extractor-network

# open an interactive SQL Server shell running against the persistent database
connect-to-persistent-database:
    docker exec -it cohort-extractor-mssql /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P 'Your_password123!'

# Full set of tests run by CI
test: test-all

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

    pytest -m integration {{ ARGS }}

# run the smoke tests only. Optional args are passed to pytest
test-smoke ARGS="": build-cohort-extractor
    #!/usr/bin/env bash
    set -euo pipefail
    . scripts/setup_functions
    dev_setup

    pytest -m smoke {{ ARGS }}

# run all tests including integration and smoke tests. Optional args are passed to pytest
test-all ARGS="": build-cohort-extractor
    #!/usr/bin/env bash
    set -euo pipefail

    [[ -v CI ]] && echo "::group::Run tests (click to view)" || echo "Run tests"
    . scripts/setup_functions
    dev_setup

    pytest --cov=cohortextractor --cov=tests {{ ARGS }}
    [[ -v CI ]]  && echo "::endgroup::" || echo ""


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
