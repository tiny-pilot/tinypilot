import auth
from request_parsers import errors


def parse_user_role(value):
    if not isinstance(value, str):
        raise errors.InvalidUserRoleError('Role must be a string')

    try:
        return auth.Role[value]
    except KeyError as e:
        raise errors.InvalidUserRoleError(
            'Role must be ADMIN or OPERATOR.') from e
