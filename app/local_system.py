import logging
import subprocess

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class ShutdownError(Error):
    pass


def shutdown():
    logger.info('Shutting down system')
    return _exec_shutdown(restart=True)


def restart():
    logger.info('Rebooting system')
    return _exec_shutdown(restart=True)


def _exec_shutdown(restart):
    if restart:
        param = '--restart'
    else:
        param = '--poweroff'

    result = subprocess.run(['sudo', '/sbin/shutdown', param, 'now'],
                            capture_output=True,
                            text=True)
    if 'failed' in result.stderr.lower():
        raise ShutdownError(result.stdout + result.stderr)
    else:
        if result.stdout:
            logger.info(result.stdout)
        if result.stderr:
            logger.info(result.stderr)
    return True
