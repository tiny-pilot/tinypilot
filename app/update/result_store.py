"""Manages persistent data about the result of the most recent TinyPilot update.

The update result store saves and fetches the result of the last update. Because
the TinyPilot server holds no state in memory, it relies on files stored in the
~/logs directory to record the result of the most recent update.

The happy path of the update is as follows:
1. User initiates an update
2. User queries for update status and the server reports an update is in
   progress because it can see the update process running.
3. User repeats (2) for a few minutes until the update completes.
4. At the end of the update, the update process writes an update result file.
5. The next time the user queries for update status, the server reads the
   update result file and reports the result of the update based on the file
   contents.

There are two interesting edge cases we have to handle:

1. The user has initiated an update, but the update process is not yet running.
     TinyPilot will check for a result file, and it may see results from
     previous updates, so we have to recognize them as stale and not the result
     of the update the user just initiated.
2. The update process crashed without ever writing a result file.
     This should be rare, but similarly to (1), we have to make sure we don't
     confuse the result of a previous update with the result of an update that
     never wrote a result file because it crashed.

The update result reader handles these edge cases by reading the timestamp of
the update result. For TinyPilot versions < 1.4.1, the timestamp represents the
start of the update process. For TinyPilot version >= 1.4.1, the timestamp
represents the end of the update process.

The result reader has a threshold, before which it assumes result files are from
previous update runs (_RECENT_UPDATE_THRESHOLD_SECONDS). The threshold is
currently set to eight 8 minutes. That means that the update reader will ignore
any result files that are timestamped more than 8 minutes prior to the current
time.

This solution is brittle because the 8 minutes is arbitrary, and there are still
situations where a previous update might be misinterpreted as the current result
(e.g., two updates in a row, within 8 minutes).

https://github.com/mtlynch/tinypilot/issues/597 tracks the work to replace the
update logic with a better solution.
"""

import glob
import logging
import os

import iso8601
import update.result
import utc

logger = logging.getLogger(__name__)

_RESULT_FILE_DIR = os.path.expanduser('~/logs')

# Cutoff under which an update is considered "recently" completed. It should be
# just long enough that it's the one we see right after a device reboot but not
# so long that there's risk of it being confused with the result from a later
# update attempt.
_RECENT_UPDATE_THRESHOLD_SECONDS = 60 * 8

# Result files are prefixed with UTC timestamps in ISO-8601 format.
_UPDATE_RESULT_FILENAME_FORMAT = '%s-update-result.json'


def read():
    """Reads the most recent update result, filtering results that are too old.

    Args:
        None.

    Returns:
        An update.result.Result based on the most recent update result file
        within the time threshold or None if none exist.
    """
    result_files = glob.glob(
        os.path.join(_RESULT_FILE_DIR, _UPDATE_RESULT_FILENAME_FORMAT % '*'))
    if not result_files:
        return None

    # Filenames start with a timestamp, so the last one lexicographically is the
    # most recently created file.
    most_recent_result_file = sorted(result_files)[-1]
    with open(most_recent_result_file) as result_file:
        most_recent_result = update.result.read(result_file)

    # Ignore the result if it's too old.
    delta = utc.now() - most_recent_result.timestamp
    if delta.total_seconds() > _RECENT_UPDATE_THRESHOLD_SECONDS:
        return None

    return most_recent_result


def write(result):
    result_path = os.path.join(
        _RESULT_FILE_DIR,
        _UPDATE_RESULT_FILENAME_FORMAT % iso8601.to_string(result.timestamp))
    os.makedirs(_RESULT_FILE_DIR, exist_ok=True)
    with open(result_path, 'w') as result_file:
        logger.info('Writing result file to %s', result_path)
        update.result.write(result, result_file)
