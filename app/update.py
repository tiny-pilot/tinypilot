import enum
import logging
import subprocess
import threading
import time

logger = logging.getLogger(__name__)

current_job = None


class Error(Exception):
    pass


class Status(enum.Enum):
    DONE = 0
    PENDING = 1
    TIMEOUT = 2
    ERROR = 3
    NOT_RUNNING = 4


_UPDATE_MAXIMUM_RUN_TIME = 60 * 10  # 10 minutes

EXIT_SUCCESS = 0


class UpdateJob:
    """Executes the TinyPilot update script.

    The script takes 2~4 minutes to complete.
    """

    def __init__(self):
        self.status = Status.NOT_RUNNING
        self.error = None

        self.start_time = None
        self.end_time = None

        self.process = None
        self.wait_thread = None

    def start(self):
        try:
            self.start_time = time.time()
            self.process = subprocess.Popen(
                ['sudo', '/opt/tinypilot-privileged/update'],
                stderr=subprocess.PIPE)
        except Exception as e:
            self.error = str(e)
            self.status = Status.ERROR
            raise Error(e)

        self.status = Status.PENDING
        self.wait_thread = threading.Thread(target=self.wait_for_progress)

    def wait_for_process(self):
        try:
            out, errs = self.process.communicate(
                timeout=_UPDATE_MAXIMUM_RUN_TIME)
            if self.process.returncode == EXIT_SUCCESS:
                self.status = Status.DONE
            else:
                self.status = Status.ERROR
                self.error = errs.strip()
            self.end_time = time.time()
        except subprocess.TimeoutExpired:
            self.status = Status.TIMEOUT
        except Exception as e:
            self.status = Status.ERROR
            self.error = 'An error occurred with the update job: %s' % str(e)
            self.process.kill()

    def is_running(self):
        return self.status in (Status.PENDING)

    def get_and_clear_status(self):
        """Checks and returns the status of the process.

        If the status was a "completed" status, clears the status so that
        subsequent calls indicate the job is "not running".

        Returns:
            One of the statuses in the Status enum.

            If the return value is Status.ERROR, the error will be stored in
            self.error.
        """

        last_status = self.status

        if last_status in (Status.DONE, Status.ERROR, Status.TIMEOUT):
            self.status = Status.NOT_RUNNING

        return last_status

    def get_state(self):
        """Returns the state of the update job.

        Returns:
            A tuple (status_message, start_time, end_time) containing the
            state of the job.

            status_message: string describing the current status
            start_time: datetime indicating when job started
            end_time: datetime indicating when job ended
        """

        status = self.get_and_clear_status()

        if status == Status.ERROR:
            message = 'Update job failed: %s' % self.error
        else:
            messages = {
                Status.PENDING: 'Updating',
                Status.DONE: 'Update complete',
                Status.TIMEOUT: 'Update timed out',
                Status.NOT_RUNNING: 'No update in progress',
            }
            message = messages.get(status, 'Update is an unrecognized state')

        return message, self.start_time, self.end_time


_global_job = UpdateJob()


def start_async():
    if _global_job.get_status() == Status.PENDING:
        raise Error('An update is already in progress')
    _global_job.start()


def get_current_state():
    return _global_job.get_state()
