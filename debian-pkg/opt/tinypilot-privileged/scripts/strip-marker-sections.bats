#!/bin/bash

{
  # Silence shellcheck for global bats variables.
  # https://github.com/tiny-pilot/tinypilot/issues/1718
  # shellcheck disable=SC2154
  echo "${output}" "${status}" "${lines}" >/dev/null
}

# Wrapper for invoking the script under test as command.
strip-marker-sections() {
  bash "${BATS_TEST_DIRNAME}/strip-marker-sections" "$@"
}

prints-help() { #@test
  run strip-marker-sections --help
  expected_output="$(cat << EOF
Usage: strip-marker-sections [--help] TARGET_FILE
Strips TinyPilot marker sections from a file.
  TARGET_FILE   Path to file with marker sections.
  --help        Display this help and exit.
EOF
  )"

  [[ "${status}" == 0 ]]
  [[ "${output}" == "${expected_output}" ]]
}

rejects-missing-input-arg() { #@test
  run strip-marker-sections

  [[ "${status}" == 1 ]]
  [[ "${output}" == 'Input parameter missing: target_file' ]]
}

rejects-non-existing-file() { #@test
  run strip-marker-sections foo-file.txt

  [[ "${status}" == 1 ]]
  [[ "${output}" == 'Not a file: foo-file.txt' ]]
}

rejects-non-file() { #@test
  tmp_dir="$(mktemp --directory)"
  run strip-marker-sections "${tmp_dir}"

  [[ "${status}" == 1 ]]
  [[ "${output}" == "Not a file: ${tmp_dir}" ]]
}

noop-if-file-has-no-markers() { #@test
  target_file="$(mktemp)"
  cat << EOF > "${target_file}"
line 1
line 2
line 3
EOF
  run strip-marker-sections "${target_file}"
  actual_contents="$(<"${target_file}")"
  expected_contents="$(cat << EOF
line 1
line 2
line 3
EOF
  )"

  [[ "${status}" == 0 ]]
  [[ "${output}" == "" ]]
  [[ "${actual_contents}" == "${expected_contents}" ]]
}

preserves-whitespace() { #@test
  target_file="$(mktemp)"
  cat << EOF > "${target_file}"
    x       y

  1
EOF
  run strip-marker-sections "${target_file}"
  actual_contents="$(<"${target_file}")"
  expected_contents="$(cat << EOF
    x       y

  1
EOF
  )"

  [[ "${status}" == 0 ]]
  [[ "${output}" == "" ]]
  [[ "${actual_contents}" == "${expected_contents}" ]]
}

strips-marker-section() { #@test
  target_file="$(mktemp)"
  cat << EOF > "${target_file}"
some line
some other line
# --- AUTOGENERATED BY TINYPILOT - START ---
to be stripped
# --- AUTOGENERATED BY TINYPILOT - END ---
final line
EOF
  run strip-marker-sections "${target_file}"
  actual_contents="$(<"${target_file}")"
  expected_contents="$(cat << EOF
some line
some other line
final line
EOF
  )"

  [[ "${status}" == 0 ]]
  [[ "${output}" == "" ]]
  [[ "${actual_contents}" == "${expected_contents}" ]]
}

strips-multiple-marker-sections() { #@test
  target_file="$(mktemp)"
  cat << EOF > "${target_file}"
some line
some other line
# --- AUTOGENERATED BY TINYPILOT - START ---
to be stripped
# --- AUTOGENERATED BY TINYPILOT - END ---
intermediate line
# --- AUTOGENERATED BY TINYPILOT - START ---
to be stripped too
# --- AUTOGENERATED BY TINYPILOT - END ---
final line
EOF
  run strip-marker-sections "${target_file}"
  actual_contents="$(<"${target_file}")"
  expected_contents="$(cat << EOF
some line
some other line
intermediate line
final line
EOF
  )"

  [[ "${status}" == 0 ]]
  [[ "${output}" == "" ]]
  [[ "${actual_contents}" == "${expected_contents}" ]]
}

fails-for-unmatched-start-marker() { #@test
  target_file="$(mktemp)"
  cat << EOF > "${target_file}"
some line
# --- AUTOGENERATED BY TINYPILOT - START ---
to be stripped
EOF
  run strip-marker-sections "${target_file}"
  actual_contents="$(<"${target_file}")"
  expected_contents="$(cat << EOF
some line
# --- AUTOGENERATED BY TINYPILOT - START ---
to be stripped
EOF
  )"

  [[ "${status}" == 1 ]]
  [[ "${output}" == "Unmatched start marker" ]]
  [[ "${actual_contents}" == "${expected_contents}" ]]
}

fails-for-unmatched-end-marker() { #@test
  target_file="$(mktemp)"
  cat << EOF > "${target_file}"
some line
# --- AUTOGENERATED BY TINYPILOT - END ---
final line
EOF
  run strip-marker-sections "${target_file}"
  actual_contents="$(<"${target_file}")"
  expected_contents="$(cat << EOF
some line
# --- AUTOGENERATED BY TINYPILOT - END ---
final line
EOF
  )"

  [[ "${status}" == 1 ]]
  [[ "${output}" == 'Unmatched end marker' ]]
  [[ "${actual_contents}" == "${expected_contents}" ]]
}
