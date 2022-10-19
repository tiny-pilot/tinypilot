import logging
import subprocess

import update.result_store
import update.status

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class AlreadyInProgressError(Error):
    pass


UPDATE_SCRIPT_PATH = '/opt/tinypilot-privileged/scripts/update'


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

    update.result_store.clear()

    # Ignore pylint since we're not managing the child process.
    # pylint: disable=consider-using-with
    subprocess.Popen(
        ('sudo', '/usr/sbin/service', 'tinypilot-updater', 'start'))
