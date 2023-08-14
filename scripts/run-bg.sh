#!/bin/bash
set -eou pipefail

script_dir="$( unset CDPATH && cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
env_file="$script_dir/environ.env"
container_name="$USER-ehrql-test-$(date +%Y%m%d-%H%M)"

docker run \
  --detach \
  --name "$container_name" \
  --env-file "$env_file" \
  -v "$script_dir/../:/app" \
  -v "$PWD:/workspace" \
  ghcr.io/opensafely-core/ehrql:v0 \
  "$@"

echo "docker logs -f $container_name"
exec docker logs -f "$container_name"
