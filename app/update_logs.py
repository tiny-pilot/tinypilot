import logging
import subprocess

_SCRIPT_PATH = '/opt/tinypilot-privileged/read-update-log'
logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class UpdateLogsReadError(Error):
    pass


def read():
    """Read the TinyPilot update logs.

    Args:
        None

    Returns:
        A string consisting of the stdout and stderr output from the
        read-update-log script.

    Raises:
        UpdateLogsReadError: If the script exits with a non-zero exit code.
    """
    logger.info('Running read-update-log')
    try:
        output = subprocess.check_output(['sudo', _SCRIPT_PATH],
                                         stderr=subprocess.STDOUT,
                                         universal_newlines=True)
    except subprocess.CalledProcessError as e:
        raise UpdateLogsReadError(str(e.output).strip()) from e
    logger.info('read-update-log completed successfully')
    return output
