import enum
import logging
import subprocess
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


DEFAULT_PROCESS_TIMEOUT = 60 * 10  # 10 minutes


class UpdateJob:
    """Executes the TinyPilot update script. The script takes 2~4 minutes to
    complete.
    """

    def __init__(self):
        self.start_time = time.time()
        self.end_time = None
        self.error = None

        try:
            self.proc = subprocess.Popen(
                ['sudo', '/opt/tinypilot-privileged/update'],
                stderr=subprocess.PIPE)
        except Exception as e:
            raise Error(e)

    def get_status(self):
        """Checks and returns the status of the process.

        Returns:
            One of the statuses in the Status enum.

            If the return value is Status.ERROR, the error will be stored in
            self.error.
        """

        try:
            out, err = self.proc.communicate(None, timeout=0)
        except subprocess.TimeoutExpired:
            if time.time() - self.start_time > DEFAULT_PROCESS_TIMEOUT:
                self.proc.kill()
                self.end_time = time.time()
                return Status.TIMEOUT
            return Status.PENDING

        if self.proc.returncode == 0:
            self.end_time = time.time()
            return Status.DONE

        self.error = err.strip()
        return Status.ERROR
