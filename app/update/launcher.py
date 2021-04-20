import logging
import subprocess

import update.result_reader
import update.status

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class AlreadyInProgressError(Error):
    pass


UPDATE_SCRIPT_PATH = '/opt/tinypilot-privileged/update'


def start_async():
    """Launches the update service asynchronously.

    Launches the tinypilot-update systemd service in the background. If the
    service is already running, raises an exception.

    Raises:
        AlreadyInProgressError if the update process is already running.
    """
    current_state, _ = update.status.get()
    if current_state == update.status.Status.IN_PROGRESS:
        raise AlreadyInProgressError('An update is already in progress')

    update.result_reader.clear()

    subprocess.Popen(
        ('sudo', '/usr/sbin/service', 'tinypilot-updater', 'start'))
