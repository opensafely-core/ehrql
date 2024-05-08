# Load environment variables from `.env` file
set dotenv-load := true
set positional-arguments


export VIRTUAL_ENV  := env_var_or_default("VIRTUAL_ENV", ".venv")

export BIN := VIRTUAL_ENV + if os_family() == "unix" { "/bin" } else { "/Scripts" }
export PIP := BIN + if os_family() == "unix" { "/python -m pip" } else { "/python.exe -m pip" }


alias help := list

# list available commands
list:
    @just --list


# clean up temporary files
clean:
    rm -rf .venv  # default just-managed venv

# ensure valid virtualenv
virtualenv:
    #!/usr/bin/env bash
    set -euo pipefail

    # allow users to specify python version in .env
    PYTHON_VERSION=${PYTHON_VERSION:-python3.11}

    # create venv and upgrade pip
    if [[ ! -d $VIRTUAL_ENV ]]; then
      $PYTHON_VERSION -m venv $VIRTUAL_ENV
      $PIP install --upgrade pip
    fi


# run pip-compile with our standard settings
pip-compile *ARGS: devenv
    #!/usr/bin/env bash
    set -euo pipefail

    $BIN/pip-compile --allow-unsafe --generate-hashes --strip-extras "$@"


# ensure dev and prod requirements installed and up to date
devenv: virtualenv
    #!/usr/bin/env bash
    set -euo pipefail

    for req_file in requirements.dev.txt requirements.prod.txt pyproject.minimal.toml; do
      # If we've installed this file before and the original hasn't been
      # modified since then bail early
      record_file="$VIRTUAL_ENV/$req_file"
      if [[ -e "$record_file" && "$record_file" -nt "$req_file" ]]; then
        continue
      fi

      if cmp --silent "$req_file" "$record_file"; then
        # If the timestamp has been changed but not the contents (as can happen
        # when switching branches) then just update the timestamp
        touch "$record_file"
      else
        # Otherwise actually install the requirements

        if [[ "$req_file" == *.txt ]]; then
          # --no-deps is recommended when using hashes, and also works around a
          # bug with constraints and hashes. See:
          # https://pip.pypa.io/en/stable/topics/secure-installs/#do-not-use-setuptools-directly
          $PIP install --no-deps --requirement "$req_file"
        elif [[ "$req_file" == *.toml ]]; then
          $PIP install --no-deps --editable "$(dirname "$req_file")"
        else
          echo "Unhandled file: $req_file"
          exit 1
        fi

        # Make a record of what we just installed
        cp "$req_file" "$record_file"
      fi
    done

    if [[ ! -f .git/hooks/pre-commit ]]; then
      $BIN/pre-commit install
    fi


ruff-format *args=".": devenv
    $BIN/ruff format --check {{ args }}

ruff *args=".": devenv
    $BIN/ruff check {{ args }}

# runs the various dev checks but does not change any files
check *args: devenv ruff-format ruff
    docker pull hadolint/hadolint
    docker run --rm -i hadolint/hadolint < Dockerfile

# runs the formatter and other code linting checks and fixes the files
fix: devenv
    $BIN/ruff format .
    $BIN/ruff check --fix .


# build the ehrql docker image
build-ehrql image_name="ehrql-dev" *args="":
    #!/usr/bin/env bash
    set -euo pipefail

    export BUILD_DATE=$(date -u +'%y-%m-%dT%H:%M:%SZ')
    export GITREF=$(git rev-parse --short HEAD)

    [[ -v CI ]] && echo "::group::Build ehrql Docker image (click to view)" || echo "Build ehrql Docker image"
    DOCKER_BUILDKIT=1 docker build . --build-arg BUILD_DATE="$BUILD_DATE" --build-arg GITREF="$GITREF" --tag {{ image_name }} {{ args }}
    [[ -v CI ]] && echo "::endgroup::" || echo ""


# Build a docker image that can then be used locally via the OpenSAFELY CLI. You must also change project.yaml
# in the study you're running to specify `dev` as the `ehrql` version (like `run: ehrql:dev ...`).
build-ehrql-for-os-cli: build-ehrql
    docker tag ehrql-dev ghcr.io/opensafely-core/ehrql:dev


# tear down the persistent docker containers we create to run tests again
remove-database-containers:
    docker rm --force ehrql-mssql ehrql-trino

# Create an MSSQL docker container with the TPP database schema and print
# connection strings
create-tpp-test-db: devenv
    $BIN/python -m pytest -o python_functions=create tests/lib/create_tpp_test_db.py

# Open an interactive SQL Server shell running against MSSQL.
# Only pass '-t' argument to Docker if stdin is a TTY so you can pipe a SQL
# file to this commmand as well as using it interactively.
connect-to-mssql:
    docker exec -i `[ -t 0 ] && echo '-t'` \
        ehrql-mssql \
            /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'Your_password123!' -d test

# open an interactive trino shell
connect-to-trino:
    docker exec -it ehrql-trino trino --catalog trino --schema default


###################################################################
# Testing targets
###################################################################

# Run all or some pytest tests. Optional args are passed to pytest, including the path of tests to run.
test *ARGS: devenv
    $BIN/python -m pytest "$@"

# Run the acceptance tests only. Optional args are passed to pytest.
test-acceptance *ARGS: devenv
    $BIN/python -m pytest tests/acceptance "$@"

# Run the backend validation tests only. Optional args are passed to pytest.
test-backend-validation *ARGS: devenv
    $BIN/python -m pytest tests/backend_validation "$@"

# Run the ehrql-in-docker tests only. Optional args are passed to pytest.
test-docker *ARGS: devenv
    $BIN/python -m pytest tests/docker "$@"

# Run the docs examples tests only. Optional args are passed to pytest.
test-docs-examples *ARGS: devenv
    $BIN/python -m pytest tests/docs "$@"

# Run the integration tests only. Optional args are passed to pytest.
test-integration *ARGS: devenv
    $BIN/python -m pytest tests/integration "$@"

# Run the spec tests only. Optional args are passed to pytest.
test-spec *ARGS: devenv
    $BIN/python -m pytest tests/spec "$@"

# Run the unit tests only. Optional args are passed to pytest.
test-unit *ARGS: devenv
    $BIN/python -m pytest tests/unit "$@"
    $BIN/python -m pytest --doctest-modules ehrql

# Run the generative tests only, configured to use more than the tiny default
# number of examples. Optional args are passed to pytest.
#
# Set GENTEST_DEBUG env var to see stats.
# Set GENTEST_EXAMPLES to change the number of examples generated.
# Set GENTEST_MAX_DEPTH to change the depth of generated query trees.
test-generative *ARGS: devenv
    GENTEST_EXAMPLES=${GENTEST_EXAMPLES:-200} \
    GENTEST_RANDOMIZE=${GENTEST_RANDOMIZE:-t} \
      $BIN/python -m pytest tests/generative "$@"


# Run by CI. Run all tests, checking code coverage. Optional args are passed to pytest.
# (The `@` prefix means that the script is echoed first for debugging purposes.)
@test-all *ARGS: devenv generate-docs
    #!/usr/bin/env bash
    set -euo pipefail

    GENTEST_EXAMPLES=${GENTEST_EXAMPLES:-100} \
    GENTEST_CHECK_IGNORED_ERRORS=t \
      $BIN/python -m pytest \
        --cov=ehrql \
        --cov=tests \
        --cov-report=html \
        --cov-report=term-missing:skip-covered \
        "$@"
    $BIN/python -m pytest --doctest-modules ehrql


# Take a raw failing example from Hypothesis's output and transform it into
# something valid and tractable
gentest-example-simplify *ARGS: devenv
    $BIN/python -m tests.lib.gentest_example_simplify "$@"

# Run a generative test example defined in the supplied file
gentest-example-run example *ARGS: devenv
    GENTEST_EXAMPLE_FILE='{{example}}' \
    $BIN/python -m pytest \
        tests/generative/test_query_model.py::test_query_model_example_file \
            "$@"

generate-docs OUTPUT_DIR="docs/includes/generated_docs": devenv
    $BIN/python -m ehrql.docs {{ OUTPUT_DIR }}
    echo "Generated data for documentation in {{ OUTPUT_DIR }}"

update-external-studies: devenv
    $BIN/python -m tests.acceptance.update_external_studies

update-tpp-schema: devenv
    #!/usr/bin/env bash
    set -euo pipefail

    echo 'Fetching latest tpp_schema.csv'
    $BIN/python -m tests.lib.update_tpp_schema fetch
    echo 'Building new tpp_schema.py'
    $BIN/python -m tests.lib.update_tpp_schema build

# Run the documentation server: to configure the port, append: ---dev-addr localhost:<port>
docs-serve *ARGS: devenv generate-docs
    # Run the MkDocs server with `--clean` to enforce the `exclude_docs` option.
    # This removes false positives that pertain to the autogenerated documentation includes.
    "$BIN"/mkdocs serve --clean "$@"

# Build the documentation
docs-build *ARGS: devenv generate-docs
    "$BIN"/mkdocs build --clean "$@"

# Run the snippet tests
docs-test: devenv
    echo "Not implemented here"

# Check the dataset public docs are current
docs-check-generated-docs-are-current: generate-docs
    #!/usr/bin/env bash
    set -euo pipefail

    # https://stackoverflow.com/questions/3878624/how-do-i-programmatically-determine-if-there-are-uncommitted-changes
    # git diff --exit-code won't pick up untracked files, which we also want to check for.
    if [[ -z $(git status --porcelain ./docs/includes/generated_docs/; git clean -nd ./docs/includes/generated_docs/) ]]
    then
      echo "Generated docs directory is current and free of other files/directories."
    else
      echo "Generated docs directory contains files/directories not in the repository."
      git diff ./docs/includes/generated_docs/; git clean -n ./docs/includes/generated_docs/
      exit 1
    fi

update-pledge: devenv
    #!/usr/bin/env bash
    set -euo pipefail
    URL_RECORD_FILE="bin/cosmopolitan-release-url.txt"
    ZIP_URL="$(
      $BIN/python -c \
        'import requests; print([
            i["browser_download_url"]
            for i in requests.get("https://api.github.com/repos/jart/cosmopolitan/releases/latest").json()["assets"]
            if i["name"].startswith("cosmos-") and i["name"].endswith(".zip")
        ][0])'
    )"
    echo "Latest Cosmopolitation release: $ZIP_URL"
    if grep -Fxqs "$ZIP_URL" "$URL_RECORD_FILE"; then
       echo "Already up to date."
       exit 0
    fi

    if [[ "$(uname -s)" != "Linux" ]]; then
      echo "This command can only be run on a Linux system because we need to"
      echo " \"assimilate\" `pledge` to be a regular Linux executable"
      exit 1
    fi

    echo "Downloading ..."
    TMP_FILE="$(mktemp)"
    curl --location --output "$TMP_FILE" "$ZIP_URL"
    unzip -o -j "$TMP_FILE" bin/pledge -d bin/
    rm "$TMP_FILE"

    # Rewrite the file header so it becomes a native Linux executable which we
    # can run directly without needing a shell. See:
    # https://justine.lol/apeloader/
    echo "Assimilating ..."
    bin/pledge --assimilate

    echo "Complete."
    echo "$ZIP_URL" > "$URL_RECORD_FILE"
