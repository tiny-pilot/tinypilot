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
_LOG_FILE_DIR = os.path.expanduser('~/logs')


def start_async():
    if _job.status == Status.IN_PROGRESS:
        raise AlreadyInProgressError

    threading.Thread(target=_perform_update).start()


def get_current_state():
    return _job.status, _job.error


def _perform_update():
    logger.info('Starting background thread to launch update process')
    _job.status = Status.IN_PROGRESS

    os.makedirs(_LOG_FILE_DIR)
    stdout_log, stderr_log = _generate_log_paths()

    with open(stdout_log, 'w') as stdout_file, open(stderr_log,
                                                    'w') as stderr_file:
        _run_update_script(stdout_file, stderr_file)

    logger.info('Background thread completed')
    _job.status = Status.DONE


def _generate_log_paths():
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H%M%SZ')

    stdout_log = os.path.join(_LOG_FILE_DIR, f'{timestamp}-update-stdout.log')
    stderr_log = os.path.join(_LOG_FILE_DIR, f'{timestamp}-update-stderr.log')

    return stdout_log, stderr_log


def _run_update_script(stdout_file, stderr_file):
    logger.info('Starting update process')
    try:
        proc = subprocess.run(['sudo', '/opt/tinypilot-privileged/update'],
                              stdout=stdout_file,
                              stderr=stderr_file,
                              check=True,
                              timeout=_UPDATE_MAXIMUM_RUN_TIME)
        # Don't try to kill the completed process.
        proc = None
    except subprocess.TimeoutExpired:
        logger.info('Update process timed out')
        _job.error = 'The update timed out'
    except subprocess.CalledProcessError:
        logger.info('Update process terminated with failing exit code')
        _job.error = 'The update failed'
    finally:
        if proc is not None:
            logger.info('Killing update process')
            proc.kill()
