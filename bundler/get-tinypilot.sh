#!/bin/bash

# “Mock” version of the eventual `get-tinypilot.sh` script.
# Instead of downloading the installation bundle on the fly, it expects a
# tarball named `tinypilot.tar` to be present in the same directory.

# Exit on first error.
set -e

# Exit on unset variable.
set -u

# Echo commands to stdout.
set -x

TEMP_FOLDER="$(mktemp -d)"
readonly TEMP_FOLDER

# Extract tarball to temporary folder and run install.
tar \
  --extract \
  --file tinypilot.tar \
  --directory "${TEMP_FOLDER}"
pushd "${TEMP_FOLDER}"
chmod +x install
./install
popd

# Clean up.
rm -rf "${TEMP_FOLDER}"
