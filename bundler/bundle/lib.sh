#######################################
# Adds a setting to the YAML settings file, if it's not yet defined.
# Arguments:
#   Path of target file.
#   Key to define.
#   Value to set.
# Outputs:
#   The line appended to the settings file, if the variable wasn't yet defined.
#######################################
yaml_set_if_undefined() {
  local file_path="$1"
  local key="$2"
  local value="$3"
  if ! grep --silent "^${key}:" "${file_path}"; then
    echo "${key}: ${value}" | tee --append "${file_path}"
  fi
}
