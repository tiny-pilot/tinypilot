import logging
import os.path
import subprocess

import eventlet
import flask_socketio
from flask import session

_READ_SCRIPT_PATH = '/opt/tinypilot-privileged/read-update-log'
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
        output = subprocess.check_output(['sudo', _READ_SCRIPT_PATH],
                                         stderr=subprocess.STDOUT,
                                         universal_newlines=True)
    except subprocess.CalledProcessError as e:
        raise UpdateLogsReadError(str(e.output).strip()) from e
    logger.info('read-update-log completed successfully')
    return output


class Namespace(flask_socketio.Namespace):

    def on_connect(self):
        session['update_logs'] = ''

    def on_disconnect(self):
        del session['update_logs']

    def on_read(self):
        logger.info('read event in update_logs namespace')
        while 'update_logs' in session:
            logs = read()
            common_logs = os.path.commonprefix([session['update_logs'], logs])
            new_logs = logs[len(common_logs):]
            if new_logs:
                logger.info('new_logs: %s', new_logs)
                flask_socketio.emit('read_response', new_logs)
                session['update_logs'] = logs
            eventlet.sleep(0.5)
