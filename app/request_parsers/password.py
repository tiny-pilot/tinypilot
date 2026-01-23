from request_parsers import json
from request_parsers.field_parsers import password as password_parser


def parse_password(request):
    """Parses the password from the Flask request body.

    Args:
        request: Flask request with the following field in the body:
            (str) password

    Returns:
        The parsed password as a string.

    Raises:
        InvalidPasswordError: if the password is invalid.
    """
    # pylint: disable=unbalanced-tuple-unpacking
    (password,) = json.parse_json_body(request, required_fields=('password',))

    return password_parser.parse_password(password)
