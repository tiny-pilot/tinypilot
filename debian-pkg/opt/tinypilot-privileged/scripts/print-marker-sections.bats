#!/bin/bash

{
  # Silence shellcheck for global bats variables.
  # https://github.com/tiny-pilot/tinypilot/issues/1718
  # shellcheck disable=SC2154
  echo "${output}" "${status}" "${lines}" >/dev/null
}

# Wrapper for invoking the script under test as command.
print-marker-sections() {
  bash "${BATS_TEST_DIRNAME}/print-marker-sections" "$@"
}

prints-help() { #@test
  run print-marker-sections --help
  expected_output="$(cat << EOF
Usage: print-marker-sections [--help] TARGET_FILE
Prints the contents of marker sections from a file.
  TARGET_FILE   Path to file with marker sections.
  --help        Display this help and exit.
EOF
  )"

  [[ "${status}" == 0 ]]
  [[ "${output}" == "${expected_output}" ]]
}

rejects-missing-input-arg() { #@test
  run print-marker-sections

  [[ "${status}" == 1 ]]
  [[ "${output}" == 'Input parameter missing: TARGET_FILE' ]]
}

rejects-illegal-flag() { #@test
  run print-marker-sections --foo

  [[ "${status}" == 1 ]]
  [[ "${output}" == 'Illegal option: --foo' ]]
}

rejects-non-existing-file() { #@test
  run print-marker-sections foo-file.txt

  [[ "${status}" == 1 ]]
  [[ "${output}" == 'Not a file: foo-file.txt' ]]
}

rejects-non-file() { #@test
  tmp_dir="$(mktemp --directory)"
  run print-marker-sections "${tmp_dir}"

  [[ "${status}" == 1 ]]
  [[ "${output}" == "Not a file: ${tmp_dir}" ]]
}

empty-output-if-file-has-no-markers() { #@test
  target_file="$(mktemp)"
  cat << EOF > "${target_file}"
line 1
line 2
line 3
EOF
  run print-marker-sections "${target_file}"

  [[ "${status}" == 0 ]]
  [[ "${output}" == "" ]]
}

prints-marker-section() { #@test
  target_file="$(mktemp)"
  cat << EOF > "${target_file}"
some line
some other line
# --- AUTOGENERATED BY TINYPILOT - START ---
to be
printed
# --- AUTOGENERATED BY TINYPILOT - END ---
final line
EOF
  run print-marker-sections "${target_file}"
  expected_output="$(cat << EOF
to be
printed
EOF
  )"

  [[ "${status}" == 0 ]]
  [[ "${output}" == "${expected_output}" ]]
}

prints-multiple-marker-sections() { #@test
  target_file="$(mktemp)"
  cat << EOF > "${target_file}"
some line
some other line
# --- AUTOGENERATED BY TINYPILOT - START ---
to be
# --- AUTOGENERATED BY TINYPILOT - END ---
intermediate line
# --- AUTOGENERATED BY TINYPILOT - START ---
printed
# --- AUTOGENERATED BY TINYPILOT - END ---
final line
EOF
  run print-marker-sections "${target_file}"
  expected_output="$(cat << EOF
to be
printed
EOF
  )"

  [[ "${status}" == 0 ]]
  [[ "${output}" == "${expected_output}" ]]
}

fails-for-unmatched-start-marker() { #@test
  target_file="$(mktemp)"
  cat << EOF > "${target_file}"
some line
# --- AUTOGENERATED BY TINYPILOT - START ---
to be printed
EOF
  run print-marker-sections "${target_file}"

  [[ "${status}" == 1 ]]
  [[ "${output}" == "Unmatched start marker" ]]
}

fails-for-unmatched-end-marker() { #@test
  target_file="$(mktemp)"
  cat << EOF > "${target_file}"
some line
# --- AUTOGENERATED BY TINYPILOT - END ---
final line
EOF
  run print-marker-sections "${target_file}"

  [[ "${status}" == 1 ]]
  [[ "${output}" == 'Unmatched end marker' ]]
}
