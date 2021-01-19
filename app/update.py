import logging
import subprocess

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


def update():
    """Executes the TinyPilot update script.

    The script takes 2~4 minutes to complete.

    Returns:
        True if successful.

    Raises:
        Error: The update script failed.
    """
    logger.info('Updating TinyPilot')
    result = subprocess.run(['sudo', '/opt/tinypilot-privileged/update'],
                            capture_output=True,
                            text=True)
    try:
        result.check_returncode()
    except subprocess.CalledProcessError:
        raise Error(result.stderr.strip())
    return True
