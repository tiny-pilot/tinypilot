from request_parsers import json
from request_parsers.field_parsers import password as password_parser
from request_parsers.field_parsers import username as username_parser


def parse_credentials(request):
    """Parses the credentials (username/password) from the Flask request body.

    Args:
        request: Flask request with the following fields in the body:
            (str) username
            (str) password

    Returns:
        A two-tuple consisting of the parsed username and password.

    Raises:
        InvalidUsernameError: if the username is invalid.
        InvalidPasswordError: if the password is invalid.
    """
    # pylint: disable=unbalanced-tuple-unpacking
    (username, password) = json.parse_json_body(request,
                                                required_fields=(
                                                    'username',
                                                    'password',
                                                ))

    return username_parser.parse_username(
        username), password_parser.parse_password(password)
