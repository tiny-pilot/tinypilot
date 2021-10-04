import os

SECRET_KEY_FILE = '.secret_key'


class Error(Exception):
    pass


class InvalidSecretKeyError(Error):
    pass


def read():
    """
    Read the currently saved secret key from the filesystem.

    Args:
        None

    Returns:
        The byte string content of the secret key file.

    Raises:
        IOError: If the secret key file doesn't exist yet.
    """
    with open(SECRET_KEY_FILE, 'rb') as f:  # pylint: disable=invalid-name
        return f.read()


def create():
    """
    Generate and save a secret key to the filesystem with a file permission of
    600.

    Args:
        None

    Returns:
        A string of 32 random bytes suitable for cryptographic use.
    """
    with open(SECRET_KEY_FILE, 'wb') as f:  # pylint: disable=invalid-name
        os.chmod(SECRET_KEY_FILE, 0o600)
        secret_key = os.urandom(32)
        f.write(secret_key)
        return secret_key


def get():
    """
    Get or create a secret key.

    If a secret key doesn't exist, a new one will be created and returned.

    Args:
        None

    Returns:
        The byte string content of the secret key file.
    """
    try:
        secret_key = read()
        if not secret_key:
            raise InvalidSecretKeyError
        return secret_key
    except (IOError, InvalidSecretKeyError):
        return create()
