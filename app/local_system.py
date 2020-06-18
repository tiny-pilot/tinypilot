import logging
import subprocess

_SHUTDOWN_DELAY_SECONDS = 5

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class ShutdownError(Error):
    pass


def shutdown():
    logger.info('Shutting down system')
    result = subprocess.run(
        ["/sbin/shutdown", "--poweroff",
         str(_SHUTDOWN_DELAY_SECONDS)],
        capture_output=True,
        text=True)
    if 'failed' in result.stderr.lower():
        raise ShutdownError(result.stdout + result.stderr)
    return True
