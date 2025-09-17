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
