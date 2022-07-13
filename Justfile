# just has no idiom for setting a default value for an environment variable
# so we shell out, as we need VIRTUAL_ENV in the justfile environment
export VIRTUAL_ENV  := `echo ${VIRTUAL_ENV:-.venv}`

# TODO: make it /scripts on windows?
export BIN := VIRTUAL_ENV + "/bin"
export PIP := BIN + "/python -m pip"
# enforce our chosen pip compile flags
export COMPILE := BIN + "/pip-compile --allow-unsafe --generate-hashes"


alias help := list

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


_compile src dst *args: _virtualenv
    #!/usr/bin/env bash
    # exit if src file is older than dst file (-nt = 'newer than', but we negate with || to avoid error exit code)
    test "${FORCE:-}" = "true" -o {{ src }} -nt {{ dst }} || exit 0
    $BIN/pip-compile --allow-unsafe --generate-hashes --output-file={{ dst }} {{ src }} {{ args }}


# update requirements.prod.txt if pyproject.toml has changed
requirements-prod *args:
    {{ just_executable() }} _compile pyproject.toml requirements.prod.txt {{ args }}


# update requirements.dev.txt if requirements.dev.in has changed
requirements-dev *args: requirements-prod
    {{ just_executable() }} _compile requirements.dev.in requirements.dev.txt {{ args }}


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


# upgrade dev or prod dependencies (specify package to upgrade single package, all by default)
upgrade env package="": _virtualenv
    #!/usr/bin/env bash
    opts="--upgrade"
    test -z "{{ package }}" || opts="--upgrade-package {{ package }}"
    FORCE=true {{ just_executable() }} requirements-{{ env }} $opts


# runs the format (black), sort (isort) and lint (flake8) checks but does not change any files
check: devenv
    $BIN/black --check .
    $BIN/isort --check-only --diff .
    $BIN/flake8
    $BIN/pyupgrade --py39-plus --keep-percent-format \
        $(find databuilder -name "*.py" -type f) \
        $(find tests -name "*.py" -type f)
    just docstrings

# ensure our public facing docstrings exist so we can build docs from them
docstrings: devenv
    $BIN/pydocstyle databuilder/backends/databricks.py
    $BIN/pydocstyle databuilder/backends/graphnet.py
    $BIN/pydocstyle databuilder/backends/tpp.py

    # only enforce classes are documented for the public facing docs
    $BIN/pydocstyle --add-ignore=D102,D103,D105,D106 databuilder/contracts/contracts.py

# runs the format (black) and sort (isort) checks and fixes the files
fix: devenv
    $BIN/black .
    $BIN/isort .


# build the databuilder docker image
build-databuilder:
    #!/usr/bin/env bash
    set -euo pipefail

    [[ -v CI ]] && echo "::group::Build databuilder (click to view)" || echo "Build databuilder"
    docker build . -t databuilder-dev
    [[ -v CI ]] && echo "::endgroup::" || echo ""


# tear down the persistent docker containers we create to run tests again
remove-database-containers:
    docker rm --force databuilder-mssql
    docker rm --force databuilder-spark

# open an interactive SQL Server shell running against MSSQL
connect-to-mssql:
    docker exec -it databuilder-mssql /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P 'Your_password123!'

###################################################################
# Testing targets
###################################################################

# Run all or some pytest tests. Optional args are passed to pytest, including the path of tests to run.
test *ARGS="tests": devenv
    $BIN/python -m pytest {{ ARGS }}

# Run all or some pytest tests, excluding spark tests which are slow. Optional args are passed to pytest, including the path of tests to run.
test-no-spark *ARGS="tests": devenv
    $BIN/python -m pytest -k "not spark" {{ ARGS }}

# Run the acceptance tests only. Optional args are passed to pytest.
test-acceptance *ARGS: devenv
    $BIN/python -m pytest tests/acceptance {{ ARGS }}

# Run the backend validation tests only. Optional args are passed to pytest.
test-backend-validation *ARGS: devenv
    $BIN/python -m pytest tests/backend_validation {{ ARGS }}

# Run the databuilder-in-docker tests only. Optional args are passed to pytest.
test-docker *ARGS: devenv
    $BIN/python -m pytest tests/docker {{ ARGS }}

# Run the integration tests only. Optional args are passed to pytest.
test-integration *ARGS: devenv
    $BIN/python -m pytest tests/integration {{ ARGS }}

# Run the integration tests only, excluding spark tests which are slow. Optional args are passed to pytest.
test-integration-no-spark *ARGS: devenv
    $BIN/python -m pytest tests/integration -k "not spark" {{ ARGS }}

# Run the spec tests only. Optional args are passed to pytest.
test-spec *ARGS: devenv
    $BIN/python -m pytest tests/spec {{ ARGS }}

# Run the spec tests only, excluding spark tests which are slow. Optional args are passed to pytest.
test-spec-no-spark *ARGS: devenv
    $BIN/python -m pytest tests/spec -k "not spark" {{ ARGS }}

# Run the unit tests only. Optional args are passed to pytest.
test-unit *ARGS: devenv
    $BIN/python -m pytest tests/unit {{ ARGS }}
    $BIN/python -m doctest tests/lib/in_memory/database.py

# Run the generative tests only. Optional args are passed to pytest.
#
# Set DEBUG env var to see stats. Set EXAMPLES to change the number of examples generated.
test-generative *ARGS: devenv
    $BIN/python -m pytest tests/generative {{ ARGS }}

# Run by CI. Run all tests, checking code coverage. Optional args are passed to pytest.
test-all *ARGS: devenv generate-docs
    #!/usr/bin/env bash
    set -euo pipefail

    [[ -v CI ]] && echo "::group::Run tests (click to view)" || echo "Run tests"
    $BIN/python -m pytest \
        --cov=databuilder \
        --cov=tests \
        --cov-report=html \
        --cov-report=term-missing:skip-covered \
        --hypothesis-seed=1234 \
        tests \
        {{ ARGS }}
    $BIN/python -m doctest tests/lib/in_memory/database.py
    [[ -v CI ]]  && echo "::endgroup::" || echo ""

# run scripts/dbx
dbx *ARGS:
    @$BIN/python scripts/dbx {{ ARGS }}

# ensure a working databricks cluster is set up and running
databricks-env: devenv
    $BIN/python scripts/dbx start --wait --timeout 180

databricks-test *ARGS: devenv databricks-env
    #!/usr/bin/env bash
    export DATABRICKS_URL="$($BIN/python scripts/dbx url)"
    just test {{ ARGS }}

generate-docs: devenv
    $BIN/python -m databuilder.docs >public_docs.json
    echo "Generated data for documentation."
