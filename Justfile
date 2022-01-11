# just has no idiom for setting a default value for an environment variable
# so we shell out, as we need VIRTUAL_ENV in the justfile environment
export VIRTUAL_ENV  := `echo ${VIRTUAL_ENV:-.venv}`

# TODO: make it /scripts on windows?
export BIN := VIRTUAL_ENV + "/bin"
export PIP := BIN + "/python -m pip"
# enforce our chosen pip compile flags
export COMPILE := BIN + "/pip-compile --allow-unsafe --generate-hashes"


alias help := list

test_args := "tests"

# list available commands
list:
    @just --list


# clean up temporary files
clean:
    rm -rf .venv  # default just-managed venv

# ensure valid virtualenv
_virtualenv:
    #!/usr/bin/env bash
    # allow users to specify python version in .env
    PYTHON_VERSION=${PYTHON_VERSION:-python3.9}

    # create venv and upgrade pip
    test -d $VIRTUAL_ENV || { $PYTHON_VERSION -m venv $VIRTUAL_ENV && $PIP install --upgrade pip; }

    # ensure we have pip-tools so we can run pip-compile
    test -e $BIN/pip-compile || $PIP install pip-tools


# update requirements.prod.txt if requirement.prod.in has changed
requirements-prod: _virtualenv
    #!/usr/bin/env bash
    # exit if .in file is older than .txt file (-nt = 'newer than', but we negate with || to avoid error exit code)
    test pyproject.toml -nt requirements.prod.txt || exit 0
    $COMPILE --output-file=requirements.prod.txt pyproject.toml


# update requirements.dev.txt if requirements.dev.in has changed
requirements-dev: requirements-prod
    #!/usr/bin/env bash
    # exit if .in file is older than .txt file (-nt = 'newer than', but we negate with || to avoid error exit code)
    test requirements.dev.in -nt requirements.dev.txt || exit 0
    $COMPILE --output-file=requirements.dev.txt requirements.dev.in


# ensure prod requirements installed and up to date
prodenv: requirements-prod
    #!/usr/bin/env bash
    # exit if .txt file has not changed since we installed them (-nt == "newer than', but we negate with || to avoid error exit code)
    test requirements.prod.txt -nt $VIRTUAL_ENV/.prod || exit 0

    $PIP install -r requirements.prod.txt
    touch $VIRTUAL_ENV/.prod


# && dependencies are run after the recipe has run. Needs just>=0.9.9. This is
# a killer feature over Makefiles.
#
# ensure dev requirements installed and up to date
devenv: prodenv requirements-dev && _install-precommit
    #!/usr/bin/env bash
    # exit if .txt file has not changed since we installed them (-nt == "newer than', but we negate with || to avoid error exit code)
    test requirements.dev.txt -nt $VIRTUAL_ENV/.dev || exit 0

    $PIP install -r requirements.dev.txt
    touch $VIRTUAL_ENV/.dev


# ensure precommit is installed
_install-precommit:
    #!/usr/bin/env bash
    BASE_DIR=$(git rev-parse --show-toplevel)
    test -f $BASE_DIR/.git/hooks/pre-commit || $BIN/pre-commit install


# upgrade dev or prod dependencies (all by default, specify package to upgrade single package)
upgrade env package="": _virtualenv
    #!/usr/bin/env bash
    opts="--upgrade"
    test -z "{{ package }}" || opts="--upgrade-package {{ package }}"
    $COMPILE $opts --output-file=requirements.{{ env }}.txt requirements.{{ env }}.in

# runs the format (black), sort (isort) and lint (flake8) checks but does not change any files
check: devenv
    $BIN/black --check .
    $BIN/isort --check-only --diff .
    $BIN/flake8
    $BIN/pyupgrade --py39-plus --keep-percent-format \
        $(find databuilder -name "*.py" -type f) \
        $(find tests -name "*.py" -type f)
    just docstrings
    $BIN/mypy

# ensure our public facing docstrings exist so we can build docs from them
docstrings: devenv
    $BIN/pydocstyle databuilder/backends/databricks.py
    $BIN/pydocstyle databuilder/backends/graphnet.py
    $BIN/pydocstyle databuilder/backends/tpp.py

    # only enforce classes are documented for the public facing docs
    $BIN/pydocstyle --add-ignore=D102,D103,D105,D106 databuilder/contracts/tables.py

# runs the format (black) and sort (isort) checks and fixes the files
fix: devenv
    $BIN/black .
    $BIN/isort .


# build the databuilder docker image
build-databuilder:
    #!/usr/bin/env bash
    set -euo pipefail

    [[ -v CI ]] && echo "::group::Build databuilder (click to view)" || echo "Build databuilder"
    docker build . -t databuilder
    [[ -v CI ]] && echo "::endgroup::" || echo ""


# tear down the persistent docker containers we create to run tests again
remove-database-containers:
    docker rm --force databuilder-mssql
    docker rm --force databuilder-spark

# open an interactive SQL Server shell running against MSSQL
connect-to-mssql:
    docker exec -it databuilder-mssql /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P 'Your_password123!'

# Full set of tests run by CI
test *ARGS=test_args:
    just test-all {{ ARGS }}

# run the unit tests only. Optional args are passed to pytest
test-unit *ARGS: devenv
    $BIN/python -m pytest -m "not integration" {{ ARGS }}

# run the integration tests only. Optional args are passed to pytest
test-integration *ARGS: devenv
    $BIN/python -m pytest -m integration {{ ARGS }}

# run the integration tests only, excluding spark tests which are slow. Optional args are passed to pytest
test-integration-no-spark *ARGS: devenv
    $BIN/python -m pytest -m "integration and not spark" {{ ARGS }}

# run all tests including integration tests. Optional args are passed to pytest
test-all *ARGS=test_args: devenv build-databuilder
    #!/usr/bin/env bash
    set -euo pipefail

    [[ -v CI ]] && echo "::group::Run tests (click to view)" || echo "Run tests"
    $BIN/python -m pytest \
        --cov=databuilder \
        --cov=tests \
        --cov-report=html \
        --cov-report=term-missing:skip-covered \
        {{ ARGS }}
    [[ -v CI ]]  && echo "::endgroup::" || echo ""

# run scripts/dbx
dbx *ARGS:
    @$BIN/python scripts/dbx {{ ARGS }}

# ensure a working databricks cluster is set up
databricks-env: devenv
    $BIN/python scripts/dbx create --wait --timeout 120

databricks-test *ARGS: devenv databricks-env
    #!/usr/bin/env bash
    export DATABRICKS_URL="$($BIN/python scripts/dbx url)"
    just test {{ ARGS }}

# run the validate contract test only for all backends
test-contracts: devenv
    $BIN/python -m pytest tests/backends/test_base.py -k test_validate_all_backends
