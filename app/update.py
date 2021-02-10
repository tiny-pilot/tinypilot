import datetime
import enum
import glob
import logging
import multiprocessing
import os
import signal
import subprocess

import update_result

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


_UPDATE_TIMEOUT_SECONDS = 60 * 10
# Cutoff under which an update is considered "recently" completed.
_RECENT_UPDATE_THRESHOLD_SECONDS = _UPDATE_TIMEOUT_SECONDS * 3
_LOG_FILE_DIR = os.path.expanduser('~/logs')

# Log and result files are prefixed with UTC timestamps in ISO-8601 format.
_LOG_FILENAME_FORMAT = '%s-update.log'
_UPDATE_RESULT_FILENAME_FORMAT = '%s-update-result.json'

_ISO_8601_FORMAT = '%Y-%m-%dT%H%M%SZ'
_ISO_8601_FORMAT = '%Y-%m-%dT%H%M%S%z'


def start_async():
    current_state, _ = get_current_state()
    if current_state == Status.IN_PROGRESS:
        raise AlreadyInProgressError('An update is already in progress')

    multiprocessing.Process(target=_perform_update).start()


def get_current_state():
    if _is_update_process_running():
        return Status.IN_PROGRESS, None

    recent_result = _get_latest_update_result()
    if not recent_result:
        return Status.NOT_RUNNING, None

    return Status.DONE, recent_result.error


def _is_update_process_running():
    pass


def _perform_update():
    logger.info('Starting background thread to launch update process')

    # Stay alive even if our parent process exits.
    signal.signal(signal.SIGHUP, signal.SIG_IGN)

    result = update_result.Result(success=False,
                                  error='',
                                  timestamp=datetime.datetime.utcnow())
    log_path, result_path = _generate_log_paths()
    os.makedirs(_LOG_FILE_DIR, exist_ok=True)
    try:
        with open(log_path, 'w') as log_file:
            logger.info('Saving update log to %s', log_path)
            subprocess.run(['sudo', '/opt/tinypilot-privileged/update'],
                           stdout=log_file,
                           stderr=log_file,
                           check=True,
                           timeout=_UPDATE_TIMEOUT_SECONDS)
        logger.info('Update completed successfully')
        result.success = True
    except subprocess.TimeoutExpired:
        logger.error('Update process timed out')
        result.error = 'The update timed out'
    except subprocess.CalledProcessError as e:
        logger.error('Update process terminated with failing exit code: %s',
                     str(e))
        result.error = 'The update failed: %s' % str(e)

    with open(result_path, 'w') as result_file:
        logger.info('Writing result file to %s', result_path)
        update_result.write(result, result_file)


def _generate_log_paths():
    timestamp = datetime.datetime.utcnow().strftime(_ISO_8601_FORMAT)

    log_path = os.path.join(_LOG_FILE_DIR, _LOG_FILENAME_FORMAT % timestamp)
    result_path = os.path.join(_LOG_FILE_DIR,
                               _UPDATE_RESULT_FILENAME_FORMAT % timestamp)

    return log_path, result_path


def _get_latest_update_result():
    result_files = glob.glob(
        os.path.join(_LOG_FILE_DIR, _UPDATE_RESULT_FILENAME_FORMAT % '*'))
    if not result_files:
        return None

    results = [_read_update_result_file(f) for f in result_files]
    most_recent_result = sorted(results, key=lambda r: r['timestamp'])[-1]
    delta = datetime.datetime.utcnow() - most_recent_result['timestamp']
    if delta.total_seconds() > _RECENT_UPDATE_THRESHOLD_SECONDS:
        return None

    return most_recent_result


def _read_update_result_file(result_path):
    with open(result_path) as result_file:
        return update_result.read(result_file)
