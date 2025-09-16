"""Manages user accounts and authentication checks.

This package is for managing user accounts (creating, changing or deleting
them), and for making authentication checks.

All methods that change credentials must trigger a restart of the video
streaming service. This will force all clients to re-connect, and thus to
re-authenticate. This is necessary, because otherwise connected clients would
still be able to retrieve the video stream (until they close their browser),
even when their credentials had been revoked. However, they actually should lose
access to the video stream immediately.
"""
import dataclasses
import datetime
import enum
import logging

import db.settings
import db.store
import db.users
import password as password_check
import utc
import video_service

logger = logging.getLogger(__name__)


class Role(enum.IntEnum):
    """The role denotes what a user is authorized to do on the device.

    The roles are hierarchical, so they strictly “inherit” from each other. The
    top-most role has most privileges; subsequent roles have fewer privileges:
    - ADMIN satisfies ADMIN
    - ADMIN satisfies OPERATOR
    - OPERATOR does not satisfy ADMIN
    - OPERATOR satisfies OPERATOR

    Note that the integer value of a role is an implementation detail. When
    serializing a `Role` value, for example, always use the stringified role
    name (i.e., `role.name`).

    Caution: the symbolic names (e.g., `ADMIN`) are serialized, e.g. in the DB
    and in the session. So changing existing names in the code necessitates a
    migration of all places where the roles had been serialized.
    """
    # Admins have full access to and full control of the device.
    ADMIN = 1
    # Operators can only use the device to interact with the target machine,
    # but they cannot manage the device itself.
    OPERATOR = 2


@dataclasses.dataclass
class User:
    username: str
    role: Role
    credentials_last_changed: datetime.datetime


class Error(Exception):
    pass


class OneAdminRequiredError(Error):
    """Raised to prevent that the system wouldn’t have any admin user.

    Without any admin user, the system would effectively be in a locked state
    where no one can manage the settings anymore. (Including e.g. creating a
    new admin user, or otherwise elevating a user’s privileges.)

    Note that the purpose of this error is to protect the system’s integrity as
    a whole. In addition to that, we may also carry out separate checks (e.g.
    in the API layer) to prevent the current user from accidentally locking
    themselves out individually (without violating the system integrity).
    """


def _user_from_strings(username, role, credentials_last_changed):
    """Reinstates a User object from string values (e.g., as of the DB)."""
    return User(username, Role[role],
                datetime.datetime.fromisoformat(credentials_last_changed))


def register(username, password, role):
    """Creates a new account with the given name and password.

    Args:
        username: (str)
        password: (str)
        role: (Role)

    Raises:
        db.users.UserAlreadyExistsError: If a user with the given username
            already exists on the system.
        OneAdminRequiredError
    """
    if len(get_all_accounts()) == 0 and role != Role.ADMIN:
        raise OneAdminRequiredError(
            'The very first user account on the system must have admin role.')

    logger.info_sensitive('Adding user %s with role %s', username, role)
    db.users.Users().add(username=username,
                         password_hash=password_check.generate_hash(password),
                         credentials_change_time=utc.now(),
                         role=role)
    logger.info_sensitive('Created user %s with role %s', username, role)
    video_service.restart()


def change_password(username, new_password):
    """Changes the password of the account with the given username.

    Args:
        username: (str)
        new_password: (str)

    Raises:
        db.users.UserDoesNotExistError: If a user with the given username
            does not exist on the system.
    """
    db.users.Users().change_password(
        username=username,
        new_password_hash=password_check.generate_hash(new_password),
        credentials_change_time=utc.now())
    # We're knowingly logging a user's username, which is sensitive, but we've
    # also marked the log as sensitive that can later be scrubbed.
    logger.info_sensitive(  # nosemgrep: python-logger-credential-disclosure
        'Changed password of user %s', username)
    video_service.restart()


def change_role(username, new_role):
    """Changes the role of the account with the given username.

    Args:
        username: (str)
        new_role: (Role)

    Raises:
        db.users.UserDoesNotExistError: If a user with the given username
            does not exist on the system.
        OneAdminRequiredError: If the user with the given username is the last
            remaining admin on the system.
    """
    all_admins = [u for u in get_all_accounts() if u.role == Role.ADMIN]
    if len(all_admins) == 1 and all_admins[0].username == username:
        raise OneAdminRequiredError(
            'Cannot change the role of last remaining admin user on the system.'
        )

    db.users.Users().change_role(username=username,
                                 new_role=new_role,
                                 credentials_change_time=utc.now())
    logger.info_sensitive('Changed role of user %s', username)
    video_service.restart()


def delete_account(username):
    """Deletes an account from the system.

    Args:
        username: (str)

    Raises:
        db.users.UserDoesNotExistError: If a user with the given username
            does not exist on the system.
        OneAdminRequiredError: If the user with the given username is the last
            remaining admin while other users still exist on the system.
    """
    users = get_all_accounts()
    all_admins = [u for u in users if u.role == Role.ADMIN]
    if len(users) > 1 and len(
            all_admins) == 1 and all_admins[0].username == username:
        raise OneAdminRequiredError(
            'Cannot delete last remaining admin user on the system.')

    db.users.Users().delete(username)
    logger.info_sensitive('Deleted user %s', username)
    video_service.restart()


def delete_all_accounts():
    """Deletes all accounts from the system."""
    db.users.Users().delete_all()
    logger.info('Deleted all users')
    video_service.restart()


def get_account(username):
    """Looks up a user account by their username.

    Returns:
        The user, if found (as `User` object)

    Raises:
        db.users.UserDoesNotExistError
    """
    user_data = db.users.Users().get(username)
    return _user_from_strings(*user_data)


def get_all_accounts():
    """Gets all accounts on the system.

    Returns:
        A list of all accounts (as `User` objects).
    """
    return [_user_from_strings(*u) for u in db.users.Users().get_all()]


def can_authenticate(username, password):
    """Checks whether the given credentials are valid.

    Args:
        username: (str)
        password: (str)

    Returns:
        True, if username and password match.
    """
    logger.info_sensitive('Checking authentication for user %s', username)
    password_hash = db.users.Users().get_password_hash(username)

    if not password_hash:
        logger.info_sensitive('Cannot authenticate, no such user %s', username)
        return False

    is_password_correct = password_check.verify(password, password_hash)
    if not is_password_correct:
        # We're knowingly logging a user's username, which is sensitive, but
        # we've also marked the log as sensitive that can later be scrubbed.
        logger.info_sensitive(  # nosemgrep: python-logger-credential-disclosure
            'Cannot authenticate, password not correct for user %s', username)
        return False

    return True


def is_authentication_required():
    """Checks whether authentication is required to access the system.

    Returns:
        True if users are required to authenticate.
    """
    return len(get_all_accounts()) > 0
