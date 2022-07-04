from response_parsers import json


def parse_latest_version(response):
    # pylint: disable=unbalanced-tuple-unpacking
    (version,) = json.parse_json_body(response, required_fields=['version'])
    return version
