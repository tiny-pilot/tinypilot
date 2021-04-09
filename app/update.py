import enum
import logging
import subprocess

import update_result_reader

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

    subprocess.Popen(
        ('sudo', '/usr/sbin/service', 'tinypilot-updater', 'start'))


def get_current_state():
    """Retrieves the current state of the update process.

    Checks the state of any actively running update jobs or jobs that have
    finished in the last 30 minutes and returns the status and error state.

    Returns:
        A two-tuple where the first value is a Status enum and the second is a
        string containing the error associated with a recently completed update
        job. If the job completed successfully, the error string is empty.
    """
    if _is_update_process_running():
        return Status.IN_PROGRESS, None

    recent_result = update_result_reader.read()
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
