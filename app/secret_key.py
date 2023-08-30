"""Manage a key file that Flask uses as a secret key.

Flask and Flask extensions use the SECRET_KEY config value to securely sign
security-sensitive tokens. In the context of TinyPilot, Flask uses the
SECRET_KEY to sign the session cookie and the CSRF token.

We persist the SECRET_KEY to the disk so that Flask's tokens stay valid across
server restarts or reboots.

Typical usage example:

    app.config.update(
        SECRET_KEY=secret_key.get_or_create()
    )

"""
import logging
import os
import stat

import atomic_file
import env

_SECRET_KEY_FILE = env.abs_path_in_home_dir('.flask-secret-key')
_SECRET_KEY_FILE_PERMS = 0o600
_SECRET_KEY_BYTE_LENGTH = 32

logger = logging.getLogger(__name__)


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
        if file_perms != _SECRET_KEY_FILE_PERMS:
            raise InvalidSecretKeyError(
                'The secret key file must have a file permission of 600.')
        secret_key = key_file.read()
        if len(secret_key) != _SECRET_KEY_BYTE_LENGTH:
            raise InvalidSecretKeyError(
                'The secret key value must be a string of 32 bytes.')
        return secret_key


def _create():
    """Generate and save a secret key file with a file permission of 600.

    Args:
        None

    Returns:
        A string of 32 random bytes suitable for cryptographic use.

    Raises:
        IOError: If an error occured while accessing the secret key file.
    """
    logger.info('Creating new flask secret key at %s', _SECRET_KEY_FILE)
    secret_key = os.urandom(_SECRET_KEY_BYTE_LENGTH)
    with atomic_file.create(_SECRET_KEY_FILE,
                            chmod_mode=_SECRET_KEY_FILE_PERMS) as file:
        file.write(secret_key)

    return secret_key


def get_or_create():
    """Get or (re-)create a secret key.

    If a secret key doesn't exist, a new one will be created and returned.

    If it finds the key file to be corrupted (see error cases of `_get`), it
    tries to recreate it (once). Note, this will cause all existing sessions to
    be invalidated.

    Args:
        None

    Returns:
        A string of 32 bytes.

    Raises:
        IOError: If an error occured while creating the secret key file.
    """
    try:
        return _get()
    except IOError:
        # The file doesn’t exist, so we need to create it.
        logger.info('No flask secret key found')
    except InvalidSecretKeyError:
        # The existing file is corrupt, so we first remove and then recreate it.
        logger.info('Flask secret key invalid or not readable')
        os.remove(_SECRET_KEY_FILE)

    return _create()
