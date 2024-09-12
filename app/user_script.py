import os
import re
import subprocess

_USER_SCRIPT_DIR = '/home/tinypilot/user-scripts'
_USER_SCRIPT_NAMING = re.compile(r'^[a-zA-Z0-9-_]+(\.[a-zA-Z0-9]+)?$')


class Error(Exception):
    pass


class UserScriptError(Error):
    pass


def get_all():
    if not os.path.isdir(_USER_SCRIPT_DIR):
        return []

    return sorted(
        [f for f in os.listdir(_USER_SCRIPT_DIR) if _is_user_script(f)])


def run(user_script_name):
    try:
        # Ignore pylint since we're not managing the child process.
        # pylint: disable=consider-using-with
        subprocess.Popen([
            'sudo', '/opt/tinypilot-privileged/scripts/run-user-script',
            user_script_name
        ])
    except subprocess.CalledProcessError as e:
        raise UserScriptError(str(e.output).strip()) from e


def _is_user_script(user_script):
    path = os.path.join(_USER_SCRIPT_DIR, user_script)

    # Must be regular file (and not, e.g., a folder).
    if not os.path.isfile(path):
        return False

    # Must match file name rules.
    if not _USER_SCRIPT_NAMING.search(user_script):
        return False

    # Must be executable.
    if not os.access(path, os.X_OK):
        return False

    # Must not be symlink.
    if os.path.islink(path):
        return False

    return True
