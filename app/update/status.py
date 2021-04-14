import enum
import subprocess

import update.launcher
import update.result_reader


class Status(enum.Enum):
    NOT_RUNNING = 0
    IN_PROGRESS = 1
    DONE = 2

    def __str__(self):
        return str(self.name)


def get():
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

    recent_result = update.result_reader.read()
    if not recent_result:
        return Status.NOT_RUNNING, None

    return Status.DONE, recent_result.error


def _is_update_process_running():
    lines = subprocess.check_output(
        ('ps', '-auxwe')).decode('utf-8').splitlines()
    for line in lines:
        if update.launcher.UPDATE_SCRIPT_PATH in line:
            return True
    return False
