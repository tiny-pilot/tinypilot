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
    log_path, success_path = _generate_log_paths()

    with open(log_path, 'w') as log_file:
        logger.info('Saving update log to %s', log_path)
        _run_update_script(log_file, success_path)

    logger.info('Background thread completed')
    _job.status = Status.DONE


def _generate_log_paths():
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H%M%SZ')

    log_path = os.path.join(_LOG_FILE_DIR, f'{timestamp}-update.log')
    success_path = os.path.join(_LOG_FILE_DIR,
                                f'{timestamp}-update-success.log')

    return log_path, success_path


def _run_update_script(log_file, success_path):
    logger.info('Starting update process')
    try:
        subprocess.run(['sudo', '/opt/tinypilot-privileged/update'],
                       stdout=log_file,
                       stderr=log_file,
                       check=True,
                       timeout=_UPDATE_MAXIMUM_RUN_TIME)

    except subprocess.TimeoutExpired:
        logger.info('Update process timed out')
        _job.error = 'The update timed out'
        return
    except subprocess.CalledProcessError:
        logger.info('Update process terminated with failing exit code')
        _job.error = 'The update failed'
        return

    # Create success file to record success
    with open(success_path, 'w') as _:
        logger.info('Created success file at %s', success_path)
