#!/bin/bash

# Download and install the latest version of TinyPilot Community.

# Exit on first error.
set -e

# Exit on unset variable.
set -u

# Echo commands to stdout.
set -x

# Check if the user is accidentally downgrading from TinyPilot Pro.
HAS_PRO_INSTALLED=0

SCRIPT_DIR="$(dirname "$0")"
# If they're piping this script in from stdin, guess that TinyPilot is
# in the default location.
if [[ "$SCRIPT_DIR" = "." ]]; then
  SCRIPT_DIR="/opt/tinypilot"
fi
readonly SCRIPT_DIR

# Detect TinyPilot Pro if the README file has a TinyPilot Pro header.
readonly TINYPILOT_README="${SCRIPT_DIR}/README.md"
if [[ -f "${TINYPILOT_README}" ]]; then
  if [[ "$(head -n 1 ${TINYPILOT_README})" = "# TinyPilot Pro" ]]; then
    HAS_PRO_INSTALLED=1
  fi
fi
readonly HAS_PRO_INSTALLED

if [[ "${HAS_PRO_INSTALLED}" = 1 ]]; then
  set +u # Don't exit if FORCE_DOWNGRADE is unset.
  if [[ "${FORCE_DOWNGRADE}" = 1 ]]; then
    echo "Downgrading from TinyPilot Pro to TinyPilot Community Edition"
    set -u
  else
    set +x
    printf "You are trying to downgrade from TinyPilot Pro to TinyPilot "
    printf "Community Edition.\n\n"
    printf "You probably want to update to the latest version of TinyPilot "
    printf "Pro instead:\n\n"
    printf "  /opt/tinypilot/scripts/upgrade && sudo reboot\n"
    printf "\n"
    printf "If you *really* want to downgrade to TinyPilot Community Edition, "
    printf "type the following:\n\n"
    printf "  export FORCE_DOWNGRADE=1\n\n"
    printf "And then run your previous command again.\n"
    exit 255
  fi
fi

# HACK: If we let mktemp use the default /tmp directory, the system purges the file
# before the end of the script for some reason. We use /var/tmp as a workaround.
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
