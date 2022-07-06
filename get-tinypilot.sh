#!/bin/bash

# Download and install the latest version of TinyPilot Community.

# Exit on first error.
set -e

# Exit on unset variable.
set -u

# Echo commands to stdout.
set -x

# HACK: If we let mktemp use the default /tmp directory, the system purges the
# file before the end of the script for some reason. We use /var/tmp as a
# workaround.
export TMPDIR='/var/tmp'

BUNDLE_FILENAME="$(mktemp --suffix .tgz)"
readonly BUNDLE_FILENAME

BUNDLE_DIR="$(mktemp --directory)"
readonly BUNDLE_DIR

# Remove temporary files & directories.
clean_up() {
  rm -rf "${BUNDLE_FILENAME}" "${BUNDLE_DIR}"
}

# Always clean up before exiting.
trap 'clean_up' EXIT

# Download tarball to temporary file.
HTTP_CODE="$(curl https://gk.tinypilotkvm.com/community/download/latest \
  --location \
  --output "${BUNDLE_FILENAME}" \
  --write-out '%{http_code}' \
  --silent)"
readonly HTTP_CODE
if [[ "${HTTP_CODE}" != "200" ]]; then
  echo "Failed to download tarball with HTTP response status code ${HTTP_CODE}." >&2
  exit 1
fi

# Extract tarball to temporary directory and run install.
tar \
  --gunzip \
  --extract \
  --file "${BUNDLE_FILENAME}" \
  --directory "${BUNDLE_DIR}"
pushd "${BUNDLE_DIR}"
./install
