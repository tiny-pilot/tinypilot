"""Rate limiter for the login endpoint to mitigate online brute-force attacks.

This module enforces two complementary limits on failed login attempts:

  1. Per-source-IP throttling: limits how many failed attempts a single client
     IP can make in a sliding window.
  2. Per-username lockout: after a small number of consecutive failed attempts
     against a given username, that username is temporarily locked out from
     authenticating, regardless of the source IP.

A successful login resets the per-username failure counter, but does not reset
the per-IP limit (so a legitimate user repeatedly failing then succeeding does
not unlock the IP for a different attacker on the same network).

The state is kept in-process. This is acceptable because TinyPilot runs as a
single Flask process and the attacker would be defeated by the rate limit even
if the process restarts (each restart resets the counters but the attacker’s
gain is bounded). For higher assurance, this state could be moved to the
database in the future.
"""
import logging
import threading
import time

logger = logging.getLogger(__name__)

# Per-source-IP limits.
_IP_WINDOW_SECONDS = 60 * 5  # 5 minutes.
_IP_MAX_FAILURES = 10

# Per-username limits.
_USERNAME_LOCKOUT_SECONDS = 60 * 15  # 15 minutes.
_USERNAME_MAX_FAILURES = 5


class TooManyAttemptsError(Exception):
    """Raised when the caller is currently rate-limited."""


_lock = threading.Lock()
# Maps source IP (str) -> list of failure timestamps (float, seconds since
# epoch) that fall within the sliding window.
_ip_failures = {}
# Maps username (str) -> (failure_count, lockout_until_timestamp).
_username_failures = {}


def _now():
    return time.monotonic()


def _prune_ip_failures(ip_address, now):
    """Drops failure timestamps older than the sliding window."""
    cutoff = now - _IP_WINDOW_SECONDS
    timestamps = _ip_failures.get(ip_address, [])
    fresh = [t for t in timestamps if t >= cutoff]
    if fresh:
        _ip_failures[ip_address] = fresh
    elif ip_address in _ip_failures:
        del _ip_failures[ip_address]
    return fresh


def check(ip_address, username):
    """Raises TooManyAttemptsError if the caller is currently rate-limited.

    Must be called *before* validating the password, so that we don’t leak
    information about whether the username exists or the password is correct
    when the caller is locked out.

    Args:
        ip_address: (str) The source IP of the request.
        username: (str) The username being authenticated.

    Raises:
        TooManyAttemptsError: If the IP or the username is currently
            rate-limited.
    """
    now = _now()
    with _lock:
        # Per-IP check.
        if ip_address:
            fresh = _prune_ip_failures(ip_address, now)
            if len(fresh) >= _IP_MAX_FAILURES:
                raise TooManyAttemptsError(
                    'Too many failed login attempts from this address.'
                    ' Please wait a few minutes and try again.')

        # Per-username check.
        if username:
            entry = _username_failures.get(username)
            if entry is not None:
                _, locked_until = entry
                if locked_until and now < locked_until:
                    raise TooManyAttemptsError(
                        'This account is temporarily locked due to too many'
                        ' failed login attempts. Please try again later.')


def record_failure(ip_address, username):
    """Records a failed login attempt for the given IP and username."""
    now = _now()
    with _lock:
        if ip_address:
            timestamps = _ip_failures.setdefault(ip_address, [])
            timestamps.append(now)

        if username:
            count, locked_until = _username_failures.get(username, (0, 0.0))
            # If the previous lockout has expired, start counting afresh.
            if locked_until and now >= locked_until:
                count = 0
                locked_until = 0.0
            count += 1
            if count >= _USERNAME_MAX_FAILURES:
                locked_until = now + _USERNAME_LOCKOUT_SECONDS
                # We're knowingly logging a user's username, which is
                # sensitive, but we've also marked the log as sensitive so it
                # can later be scrubbed.
                logger.info_sensitive(  # nosemgrep: python-logger-credential-disclosure
                    'Locking out user %s for %d seconds after %d failed'
                    ' login attempts', username, _USERNAME_LOCKOUT_SECONDS,
                    count)
            _username_failures[username] = (count, locked_until)


def record_success(username):
    """Clears the per-username failure counter after a successful login."""
    with _lock:
        if username in _username_failures:
            del _username_failures[username]


def reset_for_testing():
    """Test-only helper to reset all rate-limiter state."""
    with _lock:
        _ip_failures.clear()
        _username_failures.clear()
