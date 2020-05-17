#!/bin/bash
# Downloads the latest copy of the DocStringChecker plugin.

# Exit build script on first failure.
set -e

# Echo commands to stdout.
set -x

# Treat undefined variables as errors.
set -u

LINT_OUTPUT_DIR=$(dirname "$0")
LINT_OUTPUT_FILE="${LINT_OUTPUT_DIR}/lint.py"

wget \
  https://chromium.googlesource.com/chromiumos/chromite/+/master/cli/cros/lint.py?format=TEXT \
  -O - | \
  base64 --decode \
  > "$LINT_OUTPUT_FILE"

MEMOIZE_OUTPUT_DIR=$(dirname "$0")/chromite/utils
MEMOIZE_OUTPUT_FILE="${MEMOIZE_OUTPUT_DIR}/memoize.py"

wget \
  https://chromium.googlesource.com/chromiumos/chromite/+/master/utils/memoize.py?format=TEXT \
  -O - | \
  base64 --decode \
  > "$MEMOIZE_OUTPUT_FILE"