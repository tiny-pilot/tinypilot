"""Manage a static secret key on the filesystem to be used by Flask.

Flask uses the SECRET_KEY config value to securely sign the session cookie. The
secret key can also be used for any other security related needs by other Flask
extensions or by your application.

For example, the popular Flask-WTF extension uses the Flask app’s SECRET_KEY to
securely sign the CSRF token.

To avoid the session cookie (or CSRF token) from expiring when the Flask server
restarts, it is necessary to maintain a static SECRET_KEY value.

    Typical usage example:

    app.config.update(
        SECRET_KEY=secret_key.get_or_create()
    )

"""

import os
import stat

_SECRET_KEY_DIR = os.path.expanduser('~')
_SECRET_KEY_FILE = os.path.join(_SECRET_KEY_DIR, '.flask_secret_key')


class Error(Exception):
    pass


class InvalidSecretKeyError(Error):
    pass


def _get():
    """Get and validate the currently saved secret key from the filesystem.

    Args:
        None

    Returns:
        A string of 32 bytes.

    Raises:
        IOError: If the secret key file doesn't exist yet.
        InvalidSecretKeyError:
            * If the secret key file doesn't have a file permission of 600.
            * If the secret key value isn't a string of 32 bytes.
    """
    with open(_SECRET_KEY_FILE, 'rb') as key_file:
        file_perms = stat.S_IMODE(os.stat(key_file.name).st_mode)
        if file_perms != 0o600:
            raise InvalidSecretKeyError(
                'The secret key file must have a file permission of 600.')
        secret_key = key_file.read()
        if len(secret_key) != 32:
            raise InvalidSecretKeyError(
                'The secret key value must be a string of 32 bytes.')
        return secret_key


def _create():
    """Generate and save a secret key to the filesystem with a file permission
    of 600.

    Args:
        None

    Returns:
        A string of 32 random bytes suitable for cryptographic use.

    Raises:
        IOError: If an error occured while accessing the secret key file.
    """
    with open(_SECRET_KEY_FILE, 'wb') as key_file:
        os.chmod(key_file.name, 0o600)
        secret_key = os.urandom(32)
        key_file.write(secret_key)
        return secret_key


def get_or_create():
    """Get or create a secret key.

    If a secret key doesn't exist, a new one will be created and returned.

    Args:
        None

    Returns:
        A string of 32 bytes.

    Raises:
        IOError: If an error occured while creating the secret key file.
    """
    try:
        return _get()
    except (IOError, InvalidSecretKeyError):
        return _create()
