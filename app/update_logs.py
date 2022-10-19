import logging
import os.path
import subprocess

import flask_socketio

import threads

_READ_SCRIPT_PATH = '/opt/tinypilot-privileged/scripts/read-update-log'
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


def get_new_logs(prev_logs, next_logs):
    """Determine the newly appended logs.

    Args:
        prev_logs: A string of the previously captured logs.
        next_logs: A string of the subsequently captured logs.
    """
    common_logs = os.path.commonprefix([prev_logs, next_logs])
    new_logs = next_logs[len(common_logs):]
    return new_logs


class Namespace(flask_socketio.Namespace):
    """Stream the TinyPilot update logs via SocketIO.

    Once a `start` event is receieved within this SocketIO Namespace, the newly
    written update logs are streamed to all connected clients via a `logs`
    event. The update logs stop streaming once a `stop` event is receieved from
    any of the connected clients.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_streaming = False
        self.prev_logs = ''
        self.client_count = 0

    def on_start(self):
        # Only stream the update logs once.
        if self.is_streaming:
            return
        self.is_streaming = True
        while self.is_streaming:
            logs = read()
            new_logs = get_new_logs(self.prev_logs, logs)
            if new_logs:
                # Send the update logs to all connected clients.
                flask_socketio.emit('logs', new_logs, broadcast=True)
                self.prev_logs = logs
            threads.reschedule(seconds=0.5)

    def on_stop(self):
        self.is_streaming = False

    def on_connect(self):
        self.client_count += 1

    def on_disconnect(self):
        self.client_count -= 1
        # Stop streaming when the last client disconnects.
        if self.client_count == 0:
            self.is_streaming = False
