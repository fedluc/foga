#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="foga-tutorial-python-only"
BUILD_LOG="$(mktemp)"

echo "Setting up example environment for python-only"

if docker build --no-cache -t "${IMAGE_NAME}" "${SCRIPT_DIR}" >"${BUILD_LOG}" 2>&1; then
  rm -f "${BUILD_LOG}"
else
  echo "Docker image build failed. Full output follows:"
  cat "${BUILD_LOG}"
  rm -f "${BUILD_LOG}"
  exit 1
fi

echo "Environment ready."
echo "Instructions will be shown inside the container."
echo
echo "Entering container..."
echo

exec docker run --rm -it "${IMAGE_NAME}" bash -i
