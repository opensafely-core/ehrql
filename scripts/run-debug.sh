#!/bin/bash
set -eou pipefail

if [[ -z "${1:-}" ]]; then
  echo 'Runs ehrQL using the production Docker container with the local code'
  echo 'checkout mounted in and the environment loaded from `environ.env`.'
  echo
  echo 'It also mounts the current directory under `/workspace` so it can be'
  echo 'run in the checkout of a study repo to mimic production behaviour.'
  echo
  echo 'Remember to DELETE any extracted data as soon as possible after use.'
  echo
  echo 'By default it runs the container detached and tails the log file. Use'
  echo 'the `-i` flag to run interactively.'
  echo
  echo 'Additional arguments are passed to ehrQL as normal e.g.'
  echo
  echo '    cd ~/some_study_repo'
  echo '    ../ehrql/scripts/run-debug.sh generate-dataset analysis/dataset_definition.py --output test.csv'
  echo
  exit 1
fi

if [[ "$1" == "-i" ]]; then
  detached=false
  shift
else
  detached=true
fi

script_dir="$( unset CDPATH && cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd )"
ehrql_dir="$( unset CDPATH && cd "$script_dir/../" && pwd )"

env_file="$script_dir/environ.env"

container_name="$USER-ehrql-test-$(date -u +%Y%m%d-%H%M%S)"

if [[ ! -f "$env_file" ]]; then
  echo "Expecting an env file at: $env_file"
  echo
  echo "This should contain appropriate configuration values e.g."
  echo
  echo "    OPENSAFELY_BACKEND=tpp"
  echo "    TEMP_DATABASE_NAME=OPENCoronaTempTables"
  echo "    DATABASE_URL=__Your personal DB creds__"
  echo
  echo "** NOTE **"
  echo "When exercising the system for debugging/development purposes you MUST"
  echo "use your personal database credentials and NOT the system credentials."
  exit 1
fi

if $detached; then

  docker run \
    --detach \
    --name "$container_name" \
    --env-file "$env_file" \
    --volume "$ehrql_dir:/app" \
    --volume "$PWD:/workspace" \
    --user "$UID" \
    ghcr.io/opensafely-core/ehrql:v1 \
    "$@" \
    > /dev/null

  echo "Running container in background and tailing logs. Clean up with:"
  echo
  echo "    docker rm -f $container_name"
  echo
  echo "Remember to DELETE any extracted data as soon as possible after use."
  echo

  exec docker logs -f "$container_name"

else

  exec docker run \
    --rm \
    --interactive \
    --tty \
    --name "$container_name" \
    --env-file "$env_file" \
    --volume "$ehrql_dir:/app" \
    --volume "$PWD:/workspace" \
    --user "$UID" \
    ghcr.io/opensafely-core/ehrql:v1 \
    "$@"

fi
