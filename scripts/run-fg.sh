#!/bin/bash
set -eou pipefail

script_dir="$( unset CDPATH && cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
env_file="$script_dir/environ.env"

exec docker run \
  --rm -it \
  --entrypoint bash \
  --env-file "$env_file" \
  -v "$script_dir/../:/app" \
  -v "$PWD:/workspace" \
  ghcr.io/opensafely-core/ehrql:v0 \
  "$@"
