import dataclasses
import enum
import logging
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
        return self.name


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


def _run_script():
    logger.info('Setting _job.status to IN_PROGRESS')
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
            logger.info(
                f'Update process return with status code {proc.returncode}, updating _job.error'
            )
            _job.error = errs.strip()
        proc = None  # Set proc to none so we don't try to kill it in the finally block
    except subprocess.TimeoutExpired:
        logger.info('Update process timed out, updating _job.error')
        _job.error = 'The update timed out'
    except Exception as e:
        logger.error(
            f'Update process met unexpected exception {str(e)}, updating _job.error'
        )
        _job.error = str(e)
    finally:
        if proc is not None:
            logger.info('Killing update process.')
            proc.kill()

    logger.info('Setting _job.status to DONE')
    _job.status = Status.DONE


def start_async():
    if _job.status == Status.IN_PROGRESS:
        raise AlreadyInProgressError

    threading.Thread(target=_run_script).start()


def get_current_state():
    return _job.status, _job.error
