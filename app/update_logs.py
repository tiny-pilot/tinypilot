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
    """Stream the TinyPilot update logs via SocketIO.

    Once a `read` event is receieved within this SocketIO Namespace, all the
    update logs are sent to the client. While the client remains connected, the
    newly written update logs are streamed to the client every 500ms.
    """

    def on_connect(self):  # pylint: disable=no-self-use
        session['update_logs'] = {
            'prev_logs': '',
            'is_reading': False,
        }

    def on_disconnect(self):  # pylint: disable=no-self-use
        session['update_logs'] = {
            'prev_logs': '',
            'is_reading': False,
        }

    def on_read(self):  # pylint: disable=no-self-use
        session['update_logs']['is_reading'] = True
        while session['update_logs']['is_reading']:
            # Get the current update logs
            logs = read()
            # Determine where the current logs overlap with the previous logs
            common_logs = os.path.commonprefix(
                [session['update_logs']['prev_logs'], logs])
            # Determine the newly added logs
            new_logs = logs[len(common_logs):]
            if new_logs:
                flask_socketio.emit('read_response', new_logs)
                session['update_logs']['prev_logs'] = logs
            eventlet.sleep(0.5)
