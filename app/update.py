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
_LOG_FILE_DIR = os.path.expanduser('~/logs')

# Log and result files are prefixed with UTC timestamps in ISO-8601 format.
_LOG_FILENAME_FORMAT = '%s-update.log'
_UPDATE_RESULT_FILENAME_FORMAT = '%s-update-result.json'

_ISO_8601_FORMAT = '%Y-%m-%dT%H%M%S%z'


def start_async():
    current_state, _ = get_current_state()
    if current_state == Status.IN_PROGRESS:
        raise AlreadyInProgressError('An update is already in progress')

    subprocess.Popen(('/usr/sbin/service', 'tinypilot-updater', 'start'))


def get_current_state():
    if _is_update_process_running():
        return Status.IN_PROGRESS, None

    recent_result = _get_latest_update_result()
    if not recent_result:
        return Status.NOT_RUNNING, None

    return Status.DONE, recent_result.error


def get_log_path(timestamp):
    return os.path.join(_LOG_FILE_DIR, _LOG_FILENAME_FORMAT % timestamp)


def get_result_path(timestamp):
    return os.path.join(_LOG_FILE_DIR,
                        _UPDATE_RESULT_FILENAME_FORMAT % timestamp)


def _is_update_process_running():
    lines = subprocess.check_output(
        ('ps', '-auxwe')).decode('utf-8').splitlines()
    for line in lines:
        if UPDATE_SCRIPT_PATH in line:
            return True
    return False


def _get_latest_update_result():
    result_files = glob.glob(
        os.path.join(_LOG_FILE_DIR, _UPDATE_RESULT_FILENAME_FORMAT % '*'))
    if not result_files:
        return None

    results = [_read_update_result_file(f) for f in result_files]
    most_recent_result = sorted(results, key=lambda r: r.timestamp)[-1]
    delta = datetime.datetime.utcnow() - most_recent_result.timestamp
    if delta.total_seconds() > _RECENT_UPDATE_THRESHOLD_SECONDS:
        return None

    return most_recent_result


def _read_update_result_file(result_path):
    with open(result_path) as result_file:
        return update_result.read(result_file)
