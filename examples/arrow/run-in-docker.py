#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
image_name="${FOGA_EXAMPLE_IMAGE:-foga-example-arrow}"

docker build \
  -f "$repo_root/examples/arrow/Dockerfile" \
  -t "$image_name" \
  "$repo_root"

if [ "$#" -gt 0 ]; then
  cmd=("$@")
else
  cmd=(bash)
fi

docker run --rm -it "$image_name" "${cmd[@]}"
