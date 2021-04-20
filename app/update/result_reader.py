"""Reads result of the most recent TinyPilot update.

The update result reader fetches the result of the last update. Because the
TinyPilot server holds no state in memory and may be checking the status of an
update job just after restarting, it's tricky to identify the result of the
update.

The happy path of the update is as follows:

1. User initiates an update
2. User queries for update status and the server reports an update is in
   progress because it can see the update process running.
3. User repeats (2) for a few minutes until the update completes.
4. At the end of the update, the update process writes an update result file.
5. The next time the user queries for update status, the server reads the
   update result file and reports the result of the update based on the file
   contents.
"""

import glob
import os

import update.result

_RESULT_FILE_DIR = os.path.expanduser('~/logs')

# Prior to 1.4.2, each update created its own separate result file, prefixed
# with a UTC timestamp in ISO-8601.
_LEGACY_UPDATE_RESULT_FILENAME_FORMAT = '%s-update-result.json'

RESULT_PATH = os.path.join(_RESULT_FILE_DIR, 'latest-update-result.json')
RESULT_GLOB = os.path.join(_RESULT_FILE_DIR,
                           _LEGACY_UPDATE_RESULT_FILENAME_FORMAT % '*')


def read():
    """Reads the most recent update result.

    Args:
        None.

    Returns:
        An update.result.Result based on the most recent update result file
        within the time threshold or None if none exist.
    """
    try:
        with open(RESULT_PATH) as result_file:
            return update.result.read(result_file)
    except FileNotFoundError:
        # If the 1.4.2
        return _read_legacy()


def _read_legacy():
    result_files = glob.glob(
        os.path.join(_RESULT_FILE_DIR,
                     _LEGACY_UPDATE_RESULT_FILENAME_FORMAT % '*'))
    if not result_files:
        return None

    # Filenames start with a timestamp, so the last one lexicographically is the
    # most recently created file.
    most_recent_result_file = sorted(result_files)[-1]
    with open(most_recent_result_file) as result_file:
        return update.result.read(result_file)


def clear():
    result_files = glob.glob(
        os.path.join(_RESULT_FILE_DIR,
                     _LEGACY_UPDATE_RESULT_FILENAME_FORMAT % '*'))
    for result_file in result_files:
        os.remove(result_file)
