from passlib.hash import pbkdf2_sha256

# pylint fails to recognize this as a global constant.
# pylint: disable=invalid-name
_CUSTOM_PBKDF2 = pbkdf2_sha256.using(rounds=50000)

# pylint can't follow pbkdf'2 members for some reason.
# pylint: disable=no-member


def generate_hash(password):
    return _CUSTOM_PBKDF2.hash(password)


def verify(password, password_hash):
    return _CUSTOM_PBKDF2.verify(password, password_hash)


# Pre-computed hash of a value no real password can match. Used by
# `dummy_verify` to equalize timing for non-existent usernames, so an
# attacker cannot enumerate valid users by measuring auth response time.
_DUMMY_HASH = _CUSTOM_PBKDF2.hash('tinypilot-dummy-password-for-timing-only')


def dummy_verify(password):
    """Runs the same work as `verify` and always returns False.

    Exists solely to equalize response time when the requested username
    does not exist on the system.
    """
    _CUSTOM_PBKDF2.verify(password, _DUMMY_HASH)
    return False
