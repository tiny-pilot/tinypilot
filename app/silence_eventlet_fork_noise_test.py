# This test exercises private members of silence_eventlet_fork_noise (the hook
# and its captured default) and triggers eventlet's private _make_thread_handle
# directly to reproduce the production traceback.
# pylint: disable=protected-access
import sys
import types
import unittest
from unittest import mock

import silence_eventlet_fork_noise

try:
    import eventlet
    import eventlet.green.thread
    _HAS_EVENTLET = True
except ImportError:
    _HAS_EVENTLET = False


def build_unraisable_args(exception_info):
    """Build a UnraisableHookArgs-like object from sys.exc_info() output.

    UnraisableHookArgs has no public Python constructor (CPython creates
    it from C before invoking sys.unraisablehook), so tests fake it with
    a SimpleNamespace that exposes the same attributes.
    """
    return types.SimpleNamespace(
        exc_type=exception_info[0],
        exc_value=exception_info[1],
        exc_traceback=exception_info[2],
        err_msg=None,
        object=None,
    )


class ApplyTest(unittest.TestCase):

    def setUp(self):
        unraisable_hook_patch = mock.patch.object(sys, 'unraisablehook')
        self.addCleanup(unraisable_hook_patch.stop)
        unraisable_hook_patch.start()

    def test_apply_replaces_sys_unraisablehook(self):
        silence_eventlet_fork_noise.apply()
        self.assertIs(sys.unraisablehook,
                      silence_eventlet_fork_noise._silencing_unraisable_hook)

    def test_apply_is_idempotent(self):
        silence_eventlet_fork_noise.apply()
        first_hook = sys.unraisablehook
        silence_eventlet_fork_noise.apply()
        self.assertIs(sys.unraisablehook, first_hook)


class SilencingUnraisableHookTest(unittest.TestCase):

    def setUp(self):
        # Stub out the captured default hook so we can verify delegation.
        default_unraisable_hook_patch = mock.patch.object(
            silence_eventlet_fork_noise, '_default_unraisable_hook')
        self.addCleanup(default_unraisable_hook_patch.stop)
        self.mock_default_unraisable_hook = (
            default_unraisable_hook_patch.start())

    def test_unrelated_exception_is_delegated_to_default_hook(self):
        try:
            raise RuntimeError('something else')
        except RuntimeError:
            unraisable_args = build_unraisable_args(sys.exc_info())
        else:
            self.fail('expected RuntimeError to raise')

        silence_eventlet_fork_noise._silencing_unraisable_hook(unraisable_args)

        self.mock_default_unraisable_hook.assert_called_once_with(
            unraisable_args)

    def test_unrelated_assertion_error_is_delegated_to_default_hook(self):
        # AssertionError that does NOT come from eventlet's _make_thread_handle
        # should still be reported via the default hook.
        try:
            raise AssertionError('elsewhere')
        except AssertionError:
            unraisable_args = build_unraisable_args(sys.exc_info())
        else:
            self.fail('expected AssertionError to raise')

        silence_eventlet_fork_noise._silencing_unraisable_hook(unraisable_args)

        self.mock_default_unraisable_hook.assert_called_once_with(
            unraisable_args)

    @unittest.skipUnless(_HAS_EVENTLET, 'eventlet not installed')
    def test_eventlet_make_thread_handle_assertion_is_silenced(self):
        # Trigger eventlet's _make_thread_handle assertion directly so the
        # traceback genuinely passes through eventlet's source file.
        try:
            eventlet.green.thread._make_thread_handle(0xDEADBEEF)
        except AssertionError:
            unraisable_args = build_unraisable_args(sys.exc_info())
        else:
            self.fail('eventlet._make_thread_handle did not raise')

        silence_eventlet_fork_noise._silencing_unraisable_hook(unraisable_args)

        self.mock_default_unraisable_hook.assert_not_called()


if __name__ == '__main__':
    unittest.main()
