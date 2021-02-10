import datetime
import enum
import glob
import logging
import os
import subprocess

import update_result

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class AlreadyInProgressError(Error):
    pass


class Status(enum.Enum):
    NOT_RUNNING = 0
    IN_PROGRESS = 1
    DONE = 2

    def __str__(self):
        return str(self.name)


UPDATE_SCRIPT_PATH = '/opt/tinypilot-privileged/update'

# Cutoff under which an update is considered "recently" completed.
_RECENT_UPDATE_THRESHOLD_SECONDS = 60 * 30
_RESULT_FILE_DIR = os.path.expanduser('~/logs')

# Result files are prefixed with UTC timestamps in ISO-8601 format.
_UPDATE_RESULT_FILENAME_FORMAT = '%s-update-result.json'

_ISO_8601_FORMAT = '%Y-%m-%dT%H%M%SZ'


def start_async():
    current_state, _ = get_current_state()
    if current_state == Status.IN_PROGRESS:
        raise AlreadyInProgressError('An update is already in progress')

    subprocess.Popen(
        ('sudo', '/usr/sbin/service', 'tinypilot-updater', 'start'))


def get_current_state():
    if _is_update_process_running():
        return Status.IN_PROGRESS, None

    recent_result = _get_latest_update_result()
    if not recent_result:
        return Status.NOT_RUNNING, None

    return Status.DONE, recent_result.error


def get_result_path(timestamp):
    return os.path.join(
        _RESULT_FILE_DIR,
        _UPDATE_RESULT_FILENAME_FORMAT % timestamp.strftime(_ISO_8601_FORMAT))


def _is_update_process_running():
    lines = subprocess.check_output(
        ('ps', '-auxwe')).decode('utf-8').splitlines()
    for line in lines:
        if UPDATE_SCRIPT_PATH in line:
            return True
    return False


def _get_latest_update_result():
    result_files = glob.glob(
        os.path.join(_RESULT_FILE_DIR, _UPDATE_RESULT_FILENAME_FORMAT % '*'))
    if not result_files:
        return None

    # Filenames start with a timestamp, so the last one is the most recent.
    most_recent_result_file = sorted(result_files)[-1]
    with open(most_recent_result_file) as result_file:
        most_recent_result = update_result.read(result_file)

    # Ignore the result if it's too old.
    delta = datetime.datetime.utcnow() - most_recent_result.timestamp
    if delta.total_seconds() > _RECENT_UPDATE_THRESHOLD_SECONDS:
        return None

    return most_recent_result
