#!/bin/bash

# Download and install the latest version of TinyPilot Community.

{ # Prevent the script from executing until the client downloads the full file.

# Exit on first error.
set -e

# Exit on unset variable.
set -u

# Echo commands before executing them, by default to stderr.
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
  if [[ "$(head -n 1 "${TINYPILOT_README}")" = "# TinyPilot Pro" ]]; then
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

# Historically, the TinyPilot bundle was unpacked to the device's disk, where it
# persisted. Since the, we've moved to the use of a volatile RAMdisk, which
# avoids excessive writes to the filesystem. As a result, this legacy installer
# directory has been orphaned and is now removed as part of this script's
# `clean_up` function.
# https://github.com/tiny-pilot/tinypilot/issues/1357
readonly LEGACY_INSTALLER_DIR='/opt/tinypilot-updater'

readonly RAMDISK_DIR='/mnt/tinypilot-installer'
readonly BUNDLE_FILE="${RAMDISK_DIR}/bundle.tgz"
readonly INSTALLER_DIR="${RAMDISK_DIR}/installer"

# Remove temporary files & directories.
clean_up() {
  umount --lazy "${RAMDISK_DIR}" || true
  rm -rf \
    "${LEGACY_INSTALLER_DIR}" \
    "${RAMDISK_DIR}"
}

# Always clean up before exiting.
trap 'clean_up' EXIT

# Mount volatile RAMdisk.
sudo mkdir "${RAMDISK_DIR}"
sudo mount \
  --types tmpfs \
  --options size=500m \
  --source tmpfs \
  --target "${RAMDISK_DIR}" \
  --verbose

# Download tarball to RAMdisk.
HTTP_CODE="$(curl https://gk.tinypilotkvm.com/community/download/latest \
  --location \
  --output "${BUNDLE_FILE}" \
  --write-out '%{http_code}' \
  --silent)"
readonly HTTP_CODE
if [[ "${HTTP_CODE}" != "200" ]]; then
  echo "Failed to download tarball with HTTP response status code ${HTTP_CODE}." >&2
  exit 1
fi

# Extract tarball to installer directory. The installer directory and all its
# content must have root ownership.
sudo mkdir "${INSTALLER_DIR}"
sudo tar \
  --gunzip \
  --extract \
  --file "${BUNDLE_FILE}" \
  --directory "${INSTALLER_DIR}"
sudo chown root:root --recursive "${INSTALLER_DIR}"

# Remove the TinyPilot Pro Debian package to avoid version conflicts with
# the TinyPilot Community Debian package.
# https://github.com/tiny-pilot/tinypilot-pro/issues/596
if [[ "${HAS_PRO_INSTALLED}" -eq 1 ]]; then
  sudo apt-get remove tinypilot --yes || true
fi

# Run install.
pushd "${INSTALLER_DIR}"
sudo ./install

} # Prevent the script from executing until the client downloads the full file.
