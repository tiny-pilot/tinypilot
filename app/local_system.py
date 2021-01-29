import logging
import platform
import subprocess

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class ShutdownError(Error):
    pass


def hostname():
    return platform.node()


def shutdown():
    logger.info('Shutting down system')
    return _exec_shutdown(restart_after=False)


def restart():
    logger.info('Rebooting system')
    return _exec_shutdown(restart_after=True)


def _exec_shutdown(restart_after):
    if restart_after:
        param = '--reboot'
    else:
        param = '--poweroff'

    try:
        result = subprocess.run(['sudo', '/sbin/shutdown', param, 'now'],
                                capture_output=True,
                                text=True,
                                check=True)
    except subprocess.CalledProcessError as e:
        raise ShutdownError(e) from e
    if 'failed' in result.stderr.lower():
        raise ShutdownError(result.stdout + result.stderr)

    if result.stdout:
        logger.info(result.stdout)
    if result.stderr:
        logger.info(result.stderr)
    return True
