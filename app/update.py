import dataclasses
import datetime
import enum
import logging
import os
import subprocess
import threading

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class AlreadyInProgressError(Error):
    pass


class Status(enum.Enum):
    NOT_RUNNING = 0
    IN_PROGRESS = 1
    DONE = 2

    def __str__(self):
        return str(self.name)


@dataclasses.dataclass
class _UpdateJob:
    status: Status
    error: str

    def __init__(self):
        self.status = Status.NOT_RUNNING
        self.error = None


_job = _UpdateJob()

_UPDATE_MAXIMUM_RUN_TIME = 60 * 10  # 10 minutes
_EXIT_SUCCESS = 0


class LoggingLevelFilter:
    """A logging filter that only allows records at the levels we specify."""

    def __init__(self, allowed_levels):
        self._allowed_levels = allowed_levels

    def filter(self, record):
        return record.levelno in self._allowed_levels


def _redirect_logging_to_logfiles():
    """Set up logger to redirect output and errors to logfiles.

    Sets up logger by adding handlers to make it send INFO logs to an "output"
    file, and CRITICAL, ERROR, and WARNING logs to an "error" file."""

    logs_folder = os.path.expanduser('~/logs/')

    # Ensure logs folder exists.
    try:
        os.mkdir(logs_folder)
    except FileExistsError:
        pass

    timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')
    output_file = os.path.join(logs_folder, f'{timestamp}-update-output.log')
    error_file = os.path.join(logs_folder, f'{timestamp}-update-errors.log')

    # Remove existing handlers.
    for handler in logger.handlers:
        logger.removeHandler(handler)

    # Create an "output" handler that redirects INFO logs to output file.
    output_handler = logging.FileHandler(output_file)
    output_handler.setLevel(logging.INFO)
    output_handler.addFilter(LoggingLevelFilter((logging.INFO,)))
    logger.addHandler(output_handler)

    # Create an "error" handler that redirects CRITICAL, ERROR, and WARNING
    # logs to output file.
    error_handler = logging.FileHandler(error_file)
    error_handler.setLevel(logging.ERROR)
    error_handler.addFilter(
        LoggingLevelFilter((logging.CRITICAL, logging.ERROR, logging.WARNING)))
    logger.addHandler(error_handler)

    return error_file


def _run_script():
    error_file = _redirect_logging_to_logfiles()

    logger.info('Starting background thread to launch update process')
    _job.status = Status.IN_PROGRESS

    proc = None
    try:
        logger.info('Starting update process')
        proc = subprocess.Popen(['sudo', '/opt/tinypilot-privileged/update'],
                                stderr=subprocess.PIPE)

        logger.info('Waiting for update process to finish or time out')
        _, errs = proc.communicate(timeout=_UPDATE_MAXIMUM_RUN_TIME)
        if proc.returncode != _EXIT_SUCCESS:
            if isinstance(errs, bytes):
                errs = errs.decode('utf-8')
            logger.error('Update process returned with status code %d',
                         proc.returncode)
            _job.error = errs.strip()

        # Set proc to none so we don't try to kill it in the finally block
        proc = None
    except subprocess.TimeoutExpired:
        logger.info('Update process timed out')
        _job.error = 'The update timed out'
    except Exception as e:  # pylint: disable=broad-except
        with open(error_file) as file:
            _job.error = '\n\n'.join([str(e), 'Error logs:', file.read()])
    finally:
        if proc is not None:
            logger.info('Killing update process')
            proc.kill()

    logger.info('Background thread completed')
    _job.status = Status.DONE


def start_async():
    if _job.status == Status.IN_PROGRESS:
        raise AlreadyInProgressError

    threading.Thread(target=_run_script).start()


def get_current_state():
    return _job.status, _job.error
