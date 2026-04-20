#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../.." && pwd)"
image_name="${FOGA_EXAMPLE_IMAGE:-foga-example-pybind11}"

docker build \
  -f "$repo_root/examples/pybind11/Dockerfile" \
  -t "$image_name" \
  "$repo_root"

if [ "$#" -gt 0 ]; then
  cmd=("$@")
else
  cmd=(foga build --profile cpptest cpp)
fi

docker run --rm "$image_name" "${cmd[@]}"
