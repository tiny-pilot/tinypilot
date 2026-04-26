import unittest

# Importing `log` configures the custom logger class that the module under
# test relies on for `info_sensitive`.
import log  # noqa: F401  pylint: disable=unused-import
import login_rate_limit


class LoginRateLimitTest(unittest.TestCase):

    def setUp(self):
        login_rate_limit.reset_for_testing()

    def test_allows_attempts_below_limit(self):
        for _ in range(3):
            login_rate_limit.check('1.2.3.4', 'alice')
            login_rate_limit.record_failure('1.2.3.4', 'alice')

    def test_locks_username_after_threshold(self):
        for _ in range(5):
            login_rate_limit.check('1.2.3.4', 'alice')
            login_rate_limit.record_failure('1.2.3.4', 'alice')
        # The 6th attempt — even from a different IP — must be rejected.
        with self.assertRaises(login_rate_limit.TooManyAttemptsError):
            login_rate_limit.check('5.6.7.8', 'alice')

    def test_locks_ip_after_threshold(self):
        # Different usernames, same IP. The IP must get locked once enough
        # failures accumulate, regardless of the username.
        for i in range(10):
            login_rate_limit.check('1.2.3.4', f'user{i}')
            login_rate_limit.record_failure('1.2.3.4', f'user{i}')
        with self.assertRaises(login_rate_limit.TooManyAttemptsError):
            login_rate_limit.check('1.2.3.4', 'someone-new')

    def test_success_resets_username_failures(self):
        for _ in range(4):
            login_rate_limit.check('1.2.3.4', 'alice')
            login_rate_limit.record_failure('1.2.3.4', 'alice')
        login_rate_limit.record_success('alice')
        # After a successful login, the username counter is reset and the
        # account is no longer near a lockout.
        for _ in range(4):
            login_rate_limit.check('1.2.3.4', 'alice')
            login_rate_limit.record_failure('1.2.3.4', 'alice')

    def test_check_without_username_or_ip_is_noop(self):
        # An empty username/IP must not raise and must not poison shared state.
        login_rate_limit.check('', '')
        login_rate_limit.record_failure('', '')


if __name__ == '__main__':
    unittest.main()
