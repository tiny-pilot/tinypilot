import datetime
import enum
import glob
import logging
import os
import pathlib
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

RESULT_PATH = os.path.expanduser('~/logs/update-result.json')


def start_async():
    """Launches the update service asynchronously.

    Launches the tinypilot-update systemd service in the background. If the
    service is already running, raises an exception.

    Raises:
        AlreadyInProgressError if the update process is already running.
    """
    current_state, _ = get_current_state()
    if current_state == Status.IN_PROGRESS:
        raise AlreadyInProgressError('An update is already in progress')

    # Remove the result of the previous update.
    # Not sure why pylint is complaining about this...
    # pylint: disable=unexpected-keyword-arg
    pathlib.Path(RESULT_PATH).unlink(missing_ok=True)

    subprocess.Popen(
        ('sudo', '/usr/sbin/service', 'tinypilot-updater', 'start'))


def get_current_state():
    """Retrieves the current state of the update process.

    Checks the state of any actively running update jobs or the last completed
    update result.

    Returns:
        A two-tuple where the first value is a Status enum and the second is a
        string containing the error associated with a recently completed update
        job. If the job completed successfully, the error string is empty.
    """
    if _is_update_process_running():
        return Status.IN_PROGRESS, None

    recent_result = _get_update_result()
    if not recent_result:
        return Status.NOT_RUNNING, None

    return Status.DONE, recent_result.error


def _is_update_process_running():
    lines = subprocess.check_output(
        ('ps', '-auxwe')).decode('utf-8').splitlines()
    for line in lines:
        if UPDATE_SCRIPT_PATH in line:
            return True
    return False


def _get_update_result():
    try:
        with open(RESULT_PATH) as result_file:
            return update_result.read(result_file)
    except FileNotFoundError:
        return None


def _get_legacy_update_result():
    result_file_dir = pathlib.Path(RESULT_PATH).parent.absolute()
    # Pattern for update result files prior to 1.4.2, when we consolidated to
    # just a single update result file.
    legacy_update_result_pattern = '*-update-result.json'
    # Cutoff under which an update is considered "recently" completed. It should
    # be just long enough that it's the one we see right after a device reboot
    # but not so long that there's risk of it being confused with the result
    # from a later update attempt.
    legacy_update_threshold_seconds = 60 * 8

    result_files = glob.glob(
        os.path.join(result_file_dir, legacy_update_result_pattern))
    if not result_files:
        return None

    # Filenames start with a timestamp, so the last one lexicographically is the
    # most recently created file.
    most_recent_result_file = sorted(result_files)[-1]

    result_creation_time = datetime.datetime.fromtimestamp(
        pathlib.Path(most_recent_result_file).stat().st_ctime)

    # Ignore the result if it's too old.
    delta = datetime.datetime.now() - result_creation_time
    if delta.total_seconds() > legacy_update_threshold_seconds:
        return None

    with open(most_recent_result_file) as result_file:
        return update_result.read(result_file)
