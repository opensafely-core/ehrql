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
        $(find tests -not -path 'tests/acceptance/external_studies/*' -name "*.py" -type f)
    just docstrings
    docker pull hadolint/hadolint
    docker run --rm -i hadolint/hadolint < Dockerfile

# ensure our public facing docstrings exist so we can build docs from them
docstrings: devenv
    $BIN/pydocstyle databuilder/backends/tpp.py

    # only enforce classes are documented for the public facing docs
    $BIN/pydocstyle --add-ignore=D102,D103,D105,D106 databuilder/contracts/wip.py

# runs the format (black) and sort (isort) checks and fixes the files
fix: devenv
    $BIN/black .
    $BIN/isort .


# build the databuilder docker image
build-databuilder:
    #!/usr/bin/env bash
    set -euo pipefail

    [[ -v CI ]] && echo "::group::Build databuilder (click to view)" || echo "Build databuilder"
    DOCKER_BUILDKIT=1 docker build . -t databuilder-dev
    [[ -v CI ]] && echo "::endgroup::" || echo ""


# Build a docker image that can then be used locally via the OpenSAFELY CLI. You must also change project.yaml
# in the study you're running to specify `dev` as the `databuilder` version (like `run: databuilder:dev ...`).
build-databuilder-for-os-cli: build-databuilder
    docker tag databuilder-dev ghcr.io/opensafely-core/databuilder:dev


# tear down the persistent docker containers we create to run tests again
remove-database-containers:
    docker rm --force databuilder-mssql

# open an interactive SQL Server shell running against MSSQL
connect-to-mssql:
    docker exec -it databuilder-mssql /opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P 'Your_password123!'

###################################################################
# Testing targets
###################################################################

# Run all or some pytest tests. Optional args are passed to pytest, including the path of tests to run.
test *ARGS="tests": devenv
    $BIN/python -m pytest {{ ARGS }}

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

# Run the spec tests only. Optional args are passed to pytest.
test-spec *ARGS: devenv
    $BIN/python -m pytest tests/spec {{ ARGS }}

# Run the unit tests only. Optional args are passed to pytest.
test-unit *ARGS: devenv
    $BIN/python -m pytest tests/unit {{ ARGS }}
    $BIN/python -m pytest --doctest-modules databuilder

# Run the generative tests only. Optional args are passed to pytest.
#
# Set GENTEST_DEBUG env var to see stats.
# Set GENTEST_EXAMPLES to change the number of examples generated.
test-generative *ARGS: devenv
    $BIN/python -m pytest tests/generative {{ ARGS }}

# Run by CI. Run all tests, checking code coverage. Optional args are passed to pytest.
# (The `@` prefix means that the script is echoed first for debugging purposes.)
@test-all *ARGS: devenv generate-docs
    #!/usr/bin/env bash
    set -euo pipefail

    examples=${GENTEST_EXAMPLES:-200}
    [[ -v CI ]] && echo "::group::Run tests (click to view)" || echo "Run tests"
    GENTEST_EXAMPLES=$examples GENTEST_COMPREHENSIVE=t $BIN/python -m pytest \
        --cov=databuilder \
        --cov=tests \
        --cov-report=html \
        --cov-report=term-missing:skip-covered \
        --hypothesis-seed=1234 \
        {{ ARGS }}
    $BIN/python -m pytest --doctest-modules databuilder
    [[ -v CI ]]  && echo "::endgroup::" || echo ""

generate-docs OUTPUT_DIR="docs/includes/generated_docs": devenv
    $BIN/python -m databuilder.docs {{ OUTPUT_DIR }}
    echo "Generated data for documentation in {{ OUTPUT_DIR }}"

update-external-studies: devenv
    $BIN/python -m tests.acceptance.update_external_studies

# Run the documentation server: to configure the port, append: ---dev-addr localhost:<port>
docs-serve *ARGS: devenv generate-docs
    "$BIN"/mkdocs serve {{ ARGS }}

# Build the documentation
docs-build *ARGS: devenv generate-docs
    "$BIN"/mkdocs build {{ ARGS }}

# Run the snippet tests
docs-test: devenv
    #!/usr/bin/env bash
    set -euo pipefail
    for f in ./docs/snippets/*.py; do
      if [[ -z "${PYTHONPATH:-}" ]]
      then
        PYTHONPATH="{{justfile_directory()}}" "$BIN"/python "$f"
      else
        PYTHONPATH="${PYTHONPATH}:{{justfile_directory()}}" "$BIN"/python "$f"
      fi
    done

# Run the dataset definitions.
docs-check-dataset-definitions: devenv
    #!/usr/bin/env bash
    set -euo pipefail

    for f in ./docs/ehrql-tutorial-examples/*dataset_definition.py; do
      # By convention, we name dataset definition as: IDENTIFIER_DATASOURCENAME_dataset_definition.py
      DATASOURCENAME=`echo "$f" | cut -d'_' -f2`
      $BIN/python -m databuilder generate-dataset "$f" --dummy-tables "./docs/ehrql-tutorial-examples/example-data/$DATASOURCENAME/"
    done


# Check the dataset definition outputs are current
docs-check-dataset-definitions-outputs-are-current: devenv
    #!/usr/bin/env bash
    set -euo pipefail

    # https://stackoverflow.com/questions/3878624/how-do-i-programmatically-determine-if-there-are-uncommitted-changes
    # git diff --exit-code won't pick up untracked files, which we also want to check for.
    if [[ -z $(git status --porcelain ./docs/ehrql-tutorial-examples/outputs/; git clean -nd ./docs/ehrql-tutorial-examples/outputs/) ]]
    then
      echo "Dataset definition outputs directory is current and free of other files/directories."
    else
      echo "Dataset definition outputs contains files/directories not in the repository."
      exit 1
    fi


docs-build-dataset-definitions-outputs: devenv
    #!/usr/bin/env bash
    set -euo pipefail

    for f in ./docs/ehrql-tutorial-examples/*dataset_definition.py; do
      # By convention, we name dataset definition as: IDENTIFIER_DATASOURCENAME_dataset_definition.py
      DATASOURCENAME=`echo "$f" | cut -d'_' -f2`
      FILENAME="$(basename "$f" .py).csv"
      "$BIN"/python -m databuilder generate-dataset "$f" --dummy-tables "./docs/ehrql-tutorial-examples/example-data/$DATASOURCENAME/" --output "./docs/ehrql-tutorial-examples/outputs/$FILENAME"
    done

# Requires OpenSAFELY CLI and Docker installed.
# Runs all actions in the `project.yaml`
docs-build-dataset-definitions-outputs-docker-project:
    #!/usr/bin/env bash
    set -euo pipefail
    # Instead of entering the directory, We could use opensafely --project-dir
    # But we would end up with a metadata directory in this directory then.
    cd "./docs/ehrql-tutorial-examples"
    opensafely run run_all --force-run-dependencies


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
      exit 1
    fi


docs-update-tutorial-databuilder-version:
    #!/usr/bin/env bash
    set -euo pipefail

    package="opensafely-core/databuilder"

    if [ -z ${GITHUB_TOKEN+x} ]
    then
        token="$(
        curl --silent \
            "https://ghcr.io/token?scope=repository:$package:pull&service=ghcr.io" \
        | jq -r '.token'
        )"
    else
        token="$(echo $GITHUB_TOKEN | base64)"
    fi

    latest_version=$(curl --silent --header "Authorization: Bearer $token" \
      "https://ghcr.io/v2/$package/tags/list" \
      | jq -r '.tags | map(select(test("^v\\d+$"))) | max_by(. | ltrimstr("v") | tonumber)'
    )

    # replace latest version in tutorial project.yaml
    sed -Ei "s/v[0-9]\b/${latest_version}/g" docs/ehrql-tutorial-examples/project.yaml
