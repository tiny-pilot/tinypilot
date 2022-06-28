#!/bin/bash

# Download and install the latest version of TinyPilot Community.

# Exit on first error.
set -e

# Exit on unset variable.
set -u

# Echo commands to stdout.
set -x

BUNDLE_FILENAME="$(mktemp)"
readonly BUNDLE_FILENAME

BUNDLE_DIR="$(mktemp -d)"
readonly BUNDLE_DIR

# Remove temporary files & directories.
clean_up() {
  rm -rf "${BUNDLE_FILENAME}" "${BUNDLE_DIR}"
}

# Download latest tarball to temporary file.
download() {
  local HTTP_CODE
  HTTP_CODE="$(curl https://gk.tinypilotkvm.com/community/download/latest \
    --location \
    --output "${BUNDLE_FILENAME}" \
    --write-out '%{http_code}' \
    --silent)"
  if [[ "${HTTP_CODE}" != "200" ]]; then
    return 1
  fi
}

# Always clean up before exiting.
trap 'clean_up' ERR

# Download tarball to temporary file.
download

# Extract tarball to temporary folder and run install.
tar \
  --gunzip \
  --extract \
  --file "${BUNDLE_FILENAME}" \
  --directory "${BUNDLE_DIR}"
pushd "${BUNDLE_DIR}"
chmod +x install
./install
