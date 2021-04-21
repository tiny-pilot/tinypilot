"""Manages persistent data about the result of the most recent TinyPilot update.

The update result store stores and fetches the result of the last update.
Because the TinyPilot server holds no state in memory, it relies on files stored
in the ~/logs directory to record the result of the most recent update.

The flow of an update is as follows:

1. User initiates an update.
2. Server clears result files of all previous updates.
3. Server initiates the update process.
4. User queries for update status and the server reports an update is in
    progress because it can see the update process running.
5. User repeats (4) for a few minutes until the update completes.
6. At the end of the update, the update process writes an update result file.
7. The next time the user queries for update status, the server reads the
   update result file and reports the result of the update based on the file's
   contents.
"""

import glob
import logging
import os

import update.result

logger = logging.getLogger(__name__)

_RESULT_FILE_DIR = os.path.expanduser('~/logs')

_RESULT_PATH = os.path.join(_RESULT_FILE_DIR, 'latest-update-result.json')

# Prior to 1.4.2, each update created its own separate result file, prefixed
# with a UTC timestamp in ISO-8601. This glob pattern matches both the
# legacy-style file naming and the new style naming.
_RESULT_GLOB_PATTERN = os.path.join(_RESULT_FILE_DIR, '*-update-result.json')


def read():
    """Reads the most recent update result.
    Args:
        None.
    Returns:
        An update.result.Result based on the most recent update result file
        within the time threshold or None if none exist.
    """
    try:
        with open(_RESULT_PATH) as result_file:
            return update.result.read(result_file)
    except FileNotFoundError:
        # If we can't find a result file with >=1.4.2 style naming, check for
        # legacy result files.
        return _read_legacy()


def _read_legacy():
    result_files = glob.glob(_RESULT_GLOB_PATTERN)
    if not result_files:
        return None

    # Filenames start with a timestamp, so the last one lexicographically is the
    # most recently created file.
    most_recent_result_file = sorted(result_files)[-1]
    with open(most_recent_result_file) as result_file:
        return update.result.read(result_file)


def clear():
    result_files = glob.glob(_RESULT_GLOB_PATTERN)
    for result_file in result_files:
        os.remove(result_file)


def write(result):
    os.makedirs(_RESULT_FILE_DIR, exist_ok=True)
    with open(_RESULT_PATH, 'w') as result_file:
        print('Writing result file to %s' % _RESULT_PATH)
        logger.info('Writing result file to %s', _RESULT_PATH)
        update.result.write(result, result_file)
