"""Manages user sessions and determines authentication/authorization state.

The `is_valid` method deals with both anonymous (not logged-in) sessions and
with logged-in users (who possess a session cookie). It’s authoritative to
determine whether a user’s request shall be accepted or denied.

The `login` method persists the authentication state of a logged-in user via a
cryptographically secured cookie. We capture the following values in the
session cookie:
- The username, which is for identifying the user account.
- The `credentials_last_changed` timestamp at the time of the login.
"""
import datetime
import logging

import flask

import auth
import db

logger = logging.getLogger(__name__)


def login(username):
    """Starts a cookie-based session for a logged-in user.

    This method assumes that the user has been correctly authenticated and
    that a corresponding user exists in the database.

    In order to refresh a session, it’s safe to call this method repeatedly
    (i.e., without having to issue a logout beforehand).

    Args:
        username: (str) The username that the session shall be associated with.

    Raises:
        db.users.UserDoesNotExistError
    """
    user = auth.get_account(username)
    flask.session['username'] = username
    flask.session[
        'credentials_last_changed'] = user.credentials_last_changed.isoformat()
    # Persist the session even after the browser has been closed.
    flask.session.permanent = True
    logger.info_sensitive('Started session for user %s', username)


def is_auth_valid(satisfies_role=None):
    """Checks whether a session’s auth state is valid.

    This method effectively performs a combined authentication and
    authorization check (short: “auth”), while taking into account whether the
    system requires any auth check at all. Optionally and additionally, it
    checks whether the session satisfies a certain role requirement in order to
    proceed with the request.

    On a high-level, our auth policy is this:
    -> Is authentication generally required to use the system?
      - If no: ALLOW!
      - If yes -> is the session logged-in?
        - If no: DENY!
        - If yes -> is there a role requirement and does the user’s assigned
          role satisfy it?
          - If no: DENY!
          - If yes: ALLOW!

    Note: this method aims to encapsulate the aforementioned rules as strongly
    as sensibly possible, and tries to boil down the question “is the user
    allowed to proceed” to a binary yes/no outcome. That way, we free the
    call-side from conditional logic and combinatorial complexity, at the
    expense of slightly unconventional internal semantics (e.g., treating all
    sessions as having ADMIN privileges if - yet only if! - the auth
    requirement is turned off).

    Args:
        satisfies_role: (auth.Role) Optional.

    Returns:
        Bool
    """
    # If the auth requirement is turned off, then no users exist in the system.
    # In this case, the question of authentication is obsolete: every visitor
    # practically has full access to the system, just so as if they had a
    # dedicated user account with `auth.Role.ADMIN` explicitly granted to them.
    if not auth.is_authentication_required():
        return True

    # If the session does not contain any user information, it means the user
    # didn’t authenticate albeit they are required to. We deny access.
    username = get_username()
    credentials_last_changed = _get_credentials_last_changed()
    if not username or not credentials_last_changed:
        return False

    # If the user does not exist in the database, deny access. (This may occur
    # when the user account had been deleted in the meantime, i.e., after they
    # had logged in initially.)
    try:
        user = auth.get_account(username)
    except db.users.UserDoesNotExistError:
        return False

    # If the user’s credentials have changed in the meantime (i.e., since their
    # initial log-in), deny access.
    if user.credentials_last_changed != credentials_last_changed:
        # We're knowingly logging a user's username, which is sensitive, but
        # we've also marked the log as sensitive that can later be scrubbed.
        logger.info_sensitive(  # nosemgrep: python-logger-credential-disclosure
            'Session has expired due to credential change for user %s',
            user.username)
        return False

    # Optionally (if argument specified): check whether the user’s assigned
    # role satisfies the minimum role requirement for proceeding.
    if satisfies_role is not None:
        return user.role <= satisfies_role

    return True


def logout():
    """Ends the session of the currently logged-in user.

    Note: we use crypto-based sessions rather than a server-side session store,
    so this will only direct the client to clear the session cookie. It’s not a
    reliable way for enforcing a logout, though.

    No-op in case the user wasn’t logged in.
    """
    if 'username' in flask.session:
        logger.info_sensitive('Ended session for user %s',
                              flask.session['username'])
        del flask.session['username']

    if 'credentials_last_changed' in flask.session:
        del flask.session['credentials_last_changed']


def _get_credentials_last_changed():
    """Returns a timestamp or None if there is no logged-in user."""
    if 'credentials_last_changed' not in flask.session:
        return None

    return datetime.datetime.fromisoformat(
        flask.session['credentials_last_changed'])


def get_username():
    """Returns the username of the currently logged-in user.

    Returns:
        A username as a string or None if there is no logged-in user.
    """
    return flask.session.get('username')
