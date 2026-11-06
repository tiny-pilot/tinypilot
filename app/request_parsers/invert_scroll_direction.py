from request_parsers import errors
from request_parsers import json


def parse(request):
    # pylint: disable=unbalanced-tuple-unpacking
    (invert_scroll_direction,) = json.parse_json_body(
        request, required_fields=['invertScrollDirection'])

    if not isinstance(invert_scroll_direction, bool):
        raise errors.InvalidInvertScrollDirectionPropError(
            'Property `invertScrollDirection` is required and must be a '
            'boolean.')
    return invert_scroll_direction
