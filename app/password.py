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


# A pre-computed hash of a value that no real password can match. We use it
# in `dummy_verify` to keep the timing of authentication constant for users
# that don’t exist on the system, so that an attacker cannot enumerate
# valid usernames by measuring response times.
_DUMMY_HASH = _CUSTOM_PBKDF2.hash('tinypilot-dummy-password-for-timing-only')


def dummy_verify(password):
    """Performs the same work as `verify` but always returns False.

    This exists solely to equalise the response time of authentication
    attempts when the requested username doesn’t exist on the system.
    """
    # We deliberately ignore the result of `verify` and always return False.
    _CUSTOM_PBKDF2.verify(password, _DUMMY_HASH)
    return False
