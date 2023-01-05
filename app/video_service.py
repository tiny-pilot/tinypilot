import logging
import subprocess

import flask

logger = logging.getLogger(__name__)


def restart():
    """Restarts the video streaming services for the remote screen.

    It only triggers the restart, but it doesn’t actually wait for it to
    complete.
    """
    _restart_ustreamer()
    if flask.current_app.config.get('USE_WEBRTC_REMOTE_SCREEN', False):
        _restart_janus()


def _restart_ustreamer():
    """Restarts uStreamer in a best-effort manner.

    In case the restart invocation failed, it ignores (but logs) the error.
    """
    logger.info('Triggering ustreamer restart...')
    try:
        subprocess.check_output(
            ['sudo', '/usr/sbin/service', 'ustreamer', 'restart'],
            stderr=subprocess.STDOUT,
            universal_newlines=True)
    except subprocess.CalledProcessError as e:
        logger.error('Failed to restart ustreamer: %s', e)
        return

    logger.info('Successfully restarted ustreamer')


def _restart_janus():
    """Restarts Janus in a best-effort manner.

    In case the restart invocation failed, it ignores (but logs) the error.
    """
    logger.info('Triggering janus restart...')
    try:
        subprocess.check_output(
            ['sudo', '/usr/sbin/service', 'janus', 'restart'],
            stderr=subprocess.STDOUT,
            universal_newlines=True)
    except subprocess.CalledProcessError as e:
        logger.error('Failed to restart janus: %s', e)
        return

    logger.info('Successfully restarted janus')
