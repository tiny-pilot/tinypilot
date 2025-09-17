from request_parsers import json
from request_parsers.field_parsers import password as password_parser
from request_parsers.field_parsers import user_role as user_role_parser
from request_parsers.field_parsers import username as username_parser


def parse(request):
    """Parses the username, password and role from the Flask request body.

    Args:
        request: Flask request with the following fields in the body:
            (str) username
            (str) password
            (str) role

    Returns:
        A three-tuple consisting of the parsed username (str), password (str),
        and role (auth.Role).

    Raises:
        InvalidUsernameError: if the username is invalid.
        InvalidPasswordError: if the password is invalid.
        InvalidUserRoleError: if the role is invalid.
    """
    # pylint: disable=unbalanced-tuple-unpacking
    (username, password,
     role) = json.parse_json_body(request,
                                  required_fields=('username', 'password',
                                                   'role'))

    return username_parser.parse_username(
        username), password_parser.parse_password(
            password), user_role_parser.parse_user_role(role)
