from request_parsers import errors
from request_parsers import json


def parse(request):
    # pylint: disable=unbalanced-tuple-unpacking
    (requires_https,) = json.parse_json_body(request,
                                             required_fields=['requiresHttps'])

    if not isinstance(requires_https, bool):
        raise errors.InvalidRequiresHttpsPropError(
            'Property `requiresHttps` is required and must be a boolean.')
    return requires_https
