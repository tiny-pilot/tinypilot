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
# persisted. Since then, we've moved to the use of a volatile RAMdisk, which
# avoids excessive writes to the filesystem. As a result, this legacy installer
# directory has been orphaned and is now removed as part of this script's
# `clean_up` function.
# https://github.com/tiny-pilot/tinypilot/issues/1357
readonly LEGACY_INSTALLER_DIR='/opt/tinypilot-updater'

# The RAMdisk size is broadly based on the combined size of the following:
# - The TinyPilot bundle archive
# - The unpacked TinyPilot bundle archive, after running the bundle's `install`
#     script
# - At least a 20% safety margin
# Use the following command to help you estimate a sensible size allocation:
#   du --summarize --total --bytes "${INSTALLER_DIR}" "${BUNDLE_FILE}"
readonly RAMDISK_SIZE_MIB=500

AVAILABLE_MEMORY_MIB="$(free --mebi |
  grep --fixed-strings 'Mem:' |
  tr --squeeze-repeats ' ' |
  cut --delimiter ' ' --fields 7)"
readonly AVAILABLE_MEMORY_MIB

# Assign a provisional installation directory for our `clean_up` function.
INSTALLER_DIR='/mnt/tinypilot-installer'

# Remove temporary files & directories.
clean_up() {
  sudo umount --lazy "${INSTALLER_DIR}" || true
  sudo rm -rf \
    "${LEGACY_INSTALLER_DIR}" \
    "${INSTALLER_DIR}"
}

# Always clean up before exiting.
trap 'clean_up' EXIT

# Determine the installation directory. Use RAMdisk if there is enough memory,
# otherwise, fall back to regular disk.
if (( "${AVAILABLE_MEMORY_MIB}" >= "${RAMDISK_SIZE_MIB}" )); then
  # Mount volatile RAMdisk.
  # Note: `tmpfs` can use swap space when the device's physical memory is under
  # pressure. Alternatively, we could use `ramfs` which doesn't use swap space,
  # but also doesn't enforce a filesystem size limit, unlike `tmpfs`. Considering
  # that our goal is to reduce disk writes and not necessarily eliminate them
  # altogether, the possibility of using swap space is an acceptable compromise in
  # exchange for limiting memory usage.
  # https://github.com/tiny-pilot/tinypilot/issues/1357
  sudo mkdir "${INSTALLER_DIR}"
  sudo mount \
    --types tmpfs \
    --options "size=${RAMDISK_SIZE_MIB}m" \
    --source tmpfs \
    --target "${INSTALLER_DIR}" \
    --verbose
else
  # Fall back to installing from disk.
  INSTALLER_DIR="$(mktemp --directory)"
fi
readonly INSTALLER_DIR

readonly BUNDLE_FILE="${INSTALLER_DIR}/bundle.tgz"

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
