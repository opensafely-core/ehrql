set dotenv-load := true
set positional-arguments := true

alias help := list

# List available commands
list:
    @just --list --unsorted

# Clean up temporary files
clean:
    rm -rf .venv

# Install production requirements into and remove extraneous packages from venv
prodenv:
    uv sync --no-dev

# && dependencies are run after the recipe has run. Needs just>=0.9.9. This is
# a killer feature over Makefiles.
#

# Install dev requirements into venv without removing extraneous packages
devenv: && install-precommit
    uv sync --inexact

# Ensure precommit is installed
install-precommit:
    #!/usr/bin/env bash
    set -euo pipefail

    BASE_DIR=$(git rev-parse --show-toplevel)
    test -f $BASE_DIR/.git/hooks/pre-commit || uv run pre-commit install

# Upgrade a single package to the latest version as of the cutoff in pyproject.toml
upgrade-package package: && devenv
    uv lock --upgrade-package {{ package }}

# Upgrade all packages to the latest versions as of the cutoff in pyproject.toml
upgrade-all: && devenv
    uv lock --upgrade

# Move the cutoff date in pyproject.toml to N days ago (default: 7) at midnight UTC
bump-uv-cutoff days="7":
    #!/usr/bin/env -S uvx --with tomlkit python3

    import datetime
    import tomlkit

    with open("pyproject.toml", "rb") as f:
        content = tomlkit.load(f)

    new_datetime = (
        datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=int("{{ days }}"))
    ).replace(hour=0, minute=0, second=0, microsecond=0)
    new_timestamp = new_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    if existing_timestamp := content["tool"]["uv"].get("exclude-newer"):
        if new_datetime < datetime.datetime.fromisoformat(existing_timestamp):
            print(
                f"Existing cutoff {existing_timestamp} is more recent than {new_timestamp}, not updating."
            )
            exit(0)
    content["tool"]["uv"]["exclude-newer"] = new_timestamp

    with open("pyproject.toml", "w") as f:
        tomlkit.dump(content, f)

# This is the default input command to update-dependencies action
# https://github.com/bennettoxford/update-dependencies-action

# Bump the timestamp cutoff to midnight UTC 7 days ago and upgrade all dependencies
update-dependencies: bump-uv-cutoff upgrade-all

check:
    #!/usr/bin/env bash
    set -euo pipefail

    # Make sure dates in pyproject.toml and uv.lock are in sync
    unset UV_EXCLUDE_NEWER
    rc=0
    uv lock --check || rc=$?
    if test "$rc" != "0" ; then
        echo "Timestamp cutoffs in uv.lock must match those in pyproject.toml. See DEVELOPERS.md for details and hints." >&2
        exit $rc
    fi

    failed=0

    check() {
      # Display the command we're going to run, in bold and with the "$BIN/"
      # prefix removed if present
      echo -e "\e[1m=> ${1}\e[0m"
      # Run it
      eval $1
      # Increment the counter on failure
      if [[ $? != 0 ]]; then
        failed=$((failed + 1))
        # Add spacing to separate the error output from the next check
        echo -e "\n"
      fi
    }

    check "uv run ruff format --diff --quiet ."
    check "uv run ruff check --output-format=full ."
    check "docker run --rm -i ghcr.io/hadolint/hadolint:v2.12.0-alpine < docker/Dockerfile"

    if [[ $failed > 0 ]]; then
      echo -en "\e[1;31m"
      echo "   $failed checks failed"
      echo -e "\e[0m"
      exit 1
    fi

# Fix any automatically fixable linting or formatting errors
fix:
    uv run ruff format .
    uv run ruff check --fix .
    just --fmt --unstable --justfile justfile

# Build the ehrQL docker image
build-ehrql image_name="ehrql-dev" *args="":
    #!/usr/bin/env bash
    set -euo pipefail

    export BUILD_DATE=$(date -u +'%y-%m-%dT%H:%M:%SZ')
    export GITREF=$(git rev-parse --short HEAD)

    [[ -v CI ]] && echo "::group::Build ehrql Docker image (click to view)" || echo "Build ehrql Docker image"
    DOCKER_BUILDKIT=1 docker build . \
      -f docker/Dockerfile \
      --build-arg BUILD_DATE="$BUILD_DATE" \
      --build-arg GITREF="$GITREF" \
      --build-arg UBUNTU_VERSION="$UBUNTU_VERSION" \
      --build-arg UV_VERSION="$UV_VERSION" \
      --tag {{ image_name }} {{ args }}
    [[ -v CI ]] && echo "::endgroup::" || echo ""

# Build a docker image tagged `ehrql:dev` that can be used in `project.yaml` for local testing
build-ehrql-for-os-cli: build-ehrql
    docker tag ehrql-dev ghcr.io/opensafely-core/ehrql:dev

# Tear down the persistent docker containers we create to run tests again
remove-database-containers:
    docker rm --force ehrql-mssql ehrql-trino

# Create an MSSQL docker container with the TPP database schema and print connection strings
create-tpp-test-db:
    uv run python -m pytest -o python_functions=create tests/lib/create_tpp_test_db.py

# Open an interactive SQL Server shell running against MSSQL
connect-to-mssql:
    # Only pass '-t' argument to Docker if stdin is a TTY so you can pipe a SQL
    # file to this commmand as well as using it interactively.
    docker exec -i `[ -t 0 ] && echo '-t'` \
        ehrql-mssql \
            /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P 'Your_password123!' -d test

# Open an interactive trino shell
connect-to-trino:
    docker exec -it ehrql-trino trino --catalog trino --schema default

###################################################################
# Testing targets
###################################################################

# Run all or some pytest tests
test *ARGS:
    uv run python -m pytest "$@"

# Run the acceptance tests only
test-acceptance *ARGS:
    uv run python -m pytest tests/acceptance "$@"

# Run the ehrql-in-docker tests only
test-docker *ARGS:
    uv run python -m pytest tests/docker "$@"

# Run the docs examples tests only
test-docs-examples *ARGS:
    uv run python -m pytest tests/docs "$@"

# Run the integration tests only
test-integration *ARGS:
    uv run python -m pytest tests/integration "$@"

# Run the spec tests only
test-spec *ARGS:
    uv run python -m pytest tests/spec "$@"

# Run the unit tests only
test-unit *ARGS:
    uv run python -m pytest tests/unit "$@"
    uv run python -m pytest --doctest-modules ehrql

# Run the generative tests only, configured to use more than the tiny default
# number of examples. Optional args are passed to pytest.
#
# Set GENTEST_DEBUG env var to see stats.
# Set GENTEST_EXAMPLES to change the number of examples generated.
# Set GENTEST_MAX_DEPTH to change the depth of generated query trees.
#

# Run generative tests using more than the small deterministic set of examples used in CI
test-generative *ARGS:
    GENTEST_EXAMPLES=${GENTEST_EXAMPLES:-200} \
      uv run python -m pytest tests/generative "$@"

# Run all test as they will be run in  CI (checking code coverage etc)
@test-all *ARGS: generate-docs
    #!/usr/bin/env bash
    set -euo pipefail

    GENTEST_DERANDOMIZE=t \
    GENTEST_EXAMPLES=${GENTEST_EXAMPLES:-100} \
    GENTEST_CHECK_IGNORED_ERRORS=t \
      uv run python -m pytest \
        --cov=ehrql \
        --cov=tests \
        --cov-report=html \
        --cov-report=term-missing:skip-covered \
        "$@"
    uv run python -m pytest --doctest-modules ehrql

# Convert a raw failing example from Hypothesis's output into a simplified test case
gentest-example-simplify *ARGS:
    uv run python -m tests.lib.gentest_example_simplify "$@"

# Run a generative test example defined in the supplied file
gentest-example-run example *ARGS:
    GENTEST_EXAMPLE_FILE='{{ example }}' \
    uv run python -m pytest \
        tests/generative/test_query_model.py::test_query_model_example_file \
            "$@"

generate-docs OUTPUT_DIR="docs/includes/generated_docs":
    uv run python -m ehrql.docs {{ OUTPUT_DIR }}
    echo "Generated data for documentation in {{ OUTPUT_DIR }}"

# Run the documentation server: to configure the port, append: ---dev-addr localhost:<port>
docs-serve *ARGS: generate-docs
    # Run the MkDocs server with `--clean` to enforce the `exclude_docs` option.
    # This removes false positives that pertain to the autogenerated documentation includes.
    uv run mkdocs serve --clean "$@"

# Build the documentation
docs-build *ARGS: generate-docs
    uv run mkdocs build --clean --strict "$@"

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

update-external-studies:
    uv run python -m tests.acceptance.update_external_studies

update-tpp-schema:
    #!/usr/bin/env bash
    set -euo pipefail

    echo 'Fetching latest tpp_schema.csv'
    uv run python -m tests.lib.update_tpp_schema fetch
    echo 'Building new tpp_schema.py'
    uv run python -m tests.lib.update_tpp_schema build

update-pledge:
    #!/usr/bin/env bash
    set -euo pipefail
    URL_RECORD_FILE="bin/cosmopolitan-release-url.txt"
    ZIP_URL="$(
      uv run python -c \
        'import requests; print([
            asset["browser_download_url"]
            for release in requests.get("https://api.github.com/repos/jart/cosmopolitan/releases").json()
            for asset in release["assets"]
            if asset["name"].startswith("cosmos-") and asset["name"].endswith(".zip")
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
    sh bin/pledge --assimilate

    echo "Complete."
    echo "$ZIP_URL" > "$URL_RECORD_FILE"
