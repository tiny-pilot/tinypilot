import dataclasses
import enum
import subprocess
import threading


class Error(Exception):
    pass


class Status(enum.Enum):
    DONE = 0
    IN_PROGRESS = 1
    NOT_RUNNING = 2

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
    _job.status = Status.IN_PROGRESS

    proc = None
    try:
        proc = subprocess.Popen(['sudo', '/opt/tinypilot-privileged/update'],
                                stderr=subprocess.PIPE)
        _, errs = proc.communicate(timeout=_UPDATE_MAXIMUM_RUN_TIME)
        if proc.returncode != _EXIT_SUCCESS:
            if isinstance(errs, bytes):
                errs = errs.decode('utf-8')
            _job.error = errs.strip()
    except subprocess.TimeoutExpired:
        _job.error = 'The update timed out'
    except Exception as e:
        _job.error = str(e)
    finally:
        if proc is not None:
            proc.kill()

    _job.status = Status.DONE


def start_async():
    if _job.status == Status.IN_PROGRESS:
        raise Error('An update is already in progress')

    threading.Thread(target=_run_script).start()


def get_current_state():
    return _job.status, _job.error
