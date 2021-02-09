import dataclasses
import datetime
import enum
import glob
import json
import logging
import multiprocessing
import os
import signal
import subprocess

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
_RESULT_FILENAME_FORMAT = '%s-update-result.json'

_TIMESTAMP_FORMAT = '%Y-%m-%dT%H%M%SZ'


def start_async():
    current_state, error = get_current_state()
    if == Status.IN_PROGRESS:
        raise AlreadyInProgressError

    multiprocessing.Process(target=_perform_update).start()


def get_current_state():
    if _is_update_process_running():
      return Status.IN_PROGRESS, None

    recent_result = _read_recent_update_result()
    if not recent_result:
      return Status.NOT_RUNNING, None

    return Status.DONE, recent_result.error

def _is_update_process_running():
    pass

def _get_recent_update_result():
    update_file_path = _find_recent_update_file()
    if not update_file_path:
      return None
    return _parse_recent_update_file(update_file_path)


def _find_recent_update_file():
    result_files = glob.glob(os.path.join(_LOG_FILE_DIR, _RESULT_FILENAME_FORMAT % '*'))
    if not result_files:
      return None
    most_recent_filepath = sorted(result_files)[-1]
    most_recent_filename = os.path.basename(most_recent_filepath)
    timestamp_part = most_recent_filename.split('-')[0]
    update_time = datetime.datetime.strptime(timestamp_part, '%Y-%m-%dT%H%M%SZ')
    delta = datetime.datetime.utcnow() - update_time
    if delta.total_seconds() <= _RECENT_UPDATE_THRESHOLD_SECONDS:
      return most_recent_filepath


def _parse_recent_update_file(update_file_path):
    with open(update_file_path) as update_file:
      raw_result = json.load(update_file_path)
      return {
        'success': raw_result.get('success', False),
        'error': raw_result.get('error', None),
      }

def _perform_update():
    logger.info('Starting background thread to launch update process')

    # Stay alive even if our parent process exits.
    signal.signal(signal.SIGHUP, signal.SIG_IGN)

    result = {
      'success': False,
      'error': None,
    }
    log_file, result_path = _generate_log_paths()
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
    except subprocess.CalledProcessError as ex:
        logger.error('Update process terminated with failing exit code: %s', str(ex))
        result.error = 'The update failed: %s' % str(ex)

    logger.info('Writing result file to %s', result_path)
    with open(result_path, 'w') as result_file:
        json.dump(result)


def _generate_log_paths():
    timestamp = datetime.datetime.utcnow().strftime(_TIMESTAMP_FORMAT)

    log_path = os.path.join(_LOG_FILE_DIR, _LOG_FILENAME_FORMAT % timestamp)
    result_path = os.path.join(_LOG_FILE_DIR, _RESULT_FILENAME_FORMAT % timestamp)

    return log_path, result_path
