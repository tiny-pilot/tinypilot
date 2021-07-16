import logging
import subprocess
import tempfile

import eventlet
import flask_socketio

_READ_SCRIPT_PATH = '/opt/tinypilot-privileged/read-update-log'
_STREAM_SCRIPT_PATH = '/opt/tinypilot-privileged/stream-update-log'
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


def stream(file):
    """Stream the TinyPilot update logs to a file.

    Args:
        file: The file to which stdout & stderr will be written.

    Returns:
        A Popen instance of stream-update-log process.
    """
    logger.info('Running stream-update-log')
    process = subprocess.Popen(['sudo', _STREAM_SCRIPT_PATH],
                               bufsize=0,
                               stderr=subprocess.STDOUT,
                               stdout=file)
    logger.info('stream-update-log completed successfully')
    return process


class Namespace(flask_socketio.Namespace):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.writer = None
        self.reader = None
        self.process = None

    def on_connect(self):
        logger.info('connected to update_logs namespace')
        # We can't use in-memory text streams here (i.e. io.StringIO) because
        # Popen requires a fileno.
        # We can't PIPE to stdout because Popen.stdout.read is blocking.
        # We need separate read & write handles on the same file to maintain
        # independent reading & writing positions.
        self.writer = tempfile.NamedTemporaryFile()
        self.reader = open(self.writer.name)
        self.process = stream(file=self.writer)

    def on_disconnect(self):
        logger.info('disconnected fron update_logs namespace')
        self.process.kill()
        self.reader.close()
        self.writer.close()

    def on_read(self):
        logger.info('read event in update_logs namespace')
        while True:
            try:
                data = self.reader.read()
            except ValueError:
                # ValueError: I/O operation on closed file.
                break
            if data:
                logger.info('data: %s', data)
                flask_socketio.emit('read_response', data)
            eventlet.sleep(0)
