import glob
import os

import iso8601
import update_result
import utc

# Cutoff under which an update is considered "recently" completed. It should be
# just long enough that it's the one we see right after a device reboot but not
# so long that there's risk of it being confused with the result from a later
# update attempt.
_RECENT_UPDATE_THRESHOLD_SECONDS = 60 * 8
_RESULT_FILE_DIR = os.path.expanduser('~/logs')

# Result files are prefixed with UTC timestamps in ISO-8601 format.
_UPDATE_RESULT_FILENAME_FORMAT = '%s-update-result.json'


def read():
    result_files = glob.glob(
        os.path.join(_RESULT_FILE_DIR, _UPDATE_RESULT_FILENAME_FORMAT % '*'))
    if not result_files:
        return None

    # Filenames start with a timestamp, so the last one lexicographically is the
    # most recently created file.
    most_recent_result_file = sorted(result_files)[-1]
    with open(most_recent_result_file) as result_file:
        most_recent_result = update_result.read(result_file)

    # Ignore the result if it's too old.
    delta = utc.now() - most_recent_result.timestamp
    if delta.total_seconds() > _RECENT_UPDATE_THRESHOLD_SECONDS:
        return None

    return most_recent_result


def result_path(timestamp):
    """Retrieves the associated file path for a result file for a timestamp."""
    return os.path.join(
        _RESULT_FILE_DIR,
        _UPDATE_RESULT_FILENAME_FORMAT % iso8601.to_string(timestamp))
