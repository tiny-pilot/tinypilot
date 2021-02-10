import datetime
import json

_ISO_8601_FORMAT = '%Y-%m-%dT%H%M%S%z'


def read(result_file):
    raw_result = json.load(result_file, cls=_ResultDecoder)
    return {
        'success':
            raw_result.get('success', False),
        'error':
            raw_result.get('error', None),
        'timestamp':
            raw_result.get('timestamp', datetime.datetime.utcfromtimestamp(0))
    }


def write(result, result_file):
    json.dump(result, result_file, cls=_ResultEncoder)


class _ResultEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return _datetime_to_iso8601(obj)


class _ResultDecoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self,
                                  object_hook=self._decode_object,
                                  *args,
                                  **kwargs)

    def _decode_object(self, obj):
        if 'timestamp' in obj:
            obj['timestamp'] = _iso8601_to_datetime(obj['timestamp'])
        return obj


def _datetime_to_iso8601(dt):
    return dt.strftime(_ISO_8601_FORMAT)


def _iso8601_to_datetime(iso8601_string):
    return datetime.datetime.strptime(iso8601_string, _ISO_8601_FORMAT)
