import dataclasses
import datetime
import json

import iso8601


@dataclasses.dataclass
class Result:
    # The error message for a failed update. A value of None implies the update
    # succeeded.
    error: str
    # Time at which the update completed.
    # Deprecated as of 1.4.2. We write this field but no longer read it. We're
    # keeping it around in case we failed to anticipate something in the update
    # logic and we end up needing it, but we can likely remove it after 1.4.2.
    timestamp: datetime.datetime


def read(result_file):
    """Reads an update result file.

    Parses the contents of a result file into a Result object. The file should
    have a format like:

      {
        "error": null,
        "timestamp": "2021-02-10T085735Z",
      }

    Args:
        result_file: A file containing JSON-formatted results of an update job.

    Returns:
        A Result object parsed from the file.
    """
    raw_result = json.load(result_file, cls=_ResultDecoder)
    error = raw_result.get('error', None)
    if error == '':
        error = None
    return Result(error=error,
                  timestamp=raw_result.get(
                      'timestamp', datetime.datetime.utcfromtimestamp(0)))


def write(result, result_file):
    """Serializes a Result object to a file as JSON.

    Args:
        result: A Result object containing results of an update job.
        result_file: File handle to which to serialize the result object.
    """
    json.dump(dataclasses.asdict(result), result_file, cls=_ResultEncoder)


class _ResultEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return iso8601.to_string(o)
        return o


class _ResultDecoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self,
                                  object_hook=self._decode_object,
                                  *args,
                                  **kwargs)

    def _decode_object(self, obj):
        if 'timestamp' in obj:
            obj['timestamp'] = iso8601.parse(obj['timestamp'])
        return obj
