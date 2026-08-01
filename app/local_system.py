import logging
import subprocess

import flask

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class ShutdownError(Error):
    pass


def shutdown():
    logger.info('Shutting down system')
    return _exec_shutdown(restart_after=False)


def restart():
    logger.info('Rebooting system')
    return _exec_shutdown(restart_after=True)


def _is_debug():
    return flask.current_app.debug


def _exec_shutdown(restart_after):
    # In debug mode, don't actually shut down or restart the system, as that
    # would be disruptive to a developer running the app locally.
    if _is_debug():
        logger.info('Skipping system shutdown because app is in debug mode')
        return True

    if restart_after:
        param = '--reboot'
    else:
        param = '--poweroff'

    try:
        # The command arguments are trusted because they aren't based on user
        # input.
        result = subprocess.run(  # noqa: S603
            ['/usr/bin/sudo', '/sbin/shutdown', param, 'now'],
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
