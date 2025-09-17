from request_parsers import json
from request_parsers.field_parsers import username as username_parser


def parse_delete(request):
    """Parses the username from the Flask request body.

    Args:
        request: Flask request with the username field as string in the body.

    Returns:
        (str) The parsed username.

    Raises:
        InvalidUsernameError: if the username is invalid.
    """
    # pylint: disable=unbalanced-tuple-unpacking
    (username,) = json.parse_json_body(request, required_fields=('username',))

    return username_parser.parse_username(username)
