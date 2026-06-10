"""Silence eventlet's post-fork AssertionError noise on Python 3.13.

Python 3.13's `threading._after_fork` reconstructs `_MainThread()` in
the forked child. `_MainThread.__init__` asks eventlet's monkey-patched
`_make_thread_handle` for a handle, which asserts the given thread identifier
equals the current greenlet's id, but post-fork the current greenlet
is the one that was running when `fork()` happened, not the root that
`_get_main_thread_ident()` returned. The assertion fires; Python turns
it into an `Exception ignored in:` entry on stderr; every fork path
under eventlet (`multiprocessing`, `subprocess` with `preexec_fn`, etc.)
produces log noise.

This module installs a `sys.unraisablehook` that suppresses *only* the
specific case: `AssertionError` whose traceback passes through
eventlet's `_make_thread_handle`. Anything else, unrelated
`AssertionError`s, including `AssertionError`s from
`threading._after_fork` that don't originate in eventlet's
`_make_thread_handle`, falls through to the default hook untouched.

The exception is left to fire and the threading state in the child
ends up partially broken (`_after_fork` aborts at the assertion).
That's accepted: tinypilot's child processes only run a single HID
write and exit; nothing introspects threading. Compared to a monkey
patch of `_make_thread_handle` itself, this approach is simpler and
doesn't depend on eventlet's internals.

See https://github.com/eventlet/eventlet/issues/1030 for upstream
context. The issue was closed without a merged fix; upstream
recommends migrating off eventlet rather than patching it.
"""

import sys

_default_unraisable_hook = sys.unraisablehook


def _silencing_unraisable_hook(unraisable):
    """Suppress eventlet's post-fork AssertionError; delegate the rest.

    An unraisable is suppressed only when:
    1. The exception is an `AssertionError`, AND
    2. Its traceback contains a frame whose code object is named
       `_make_thread_handle` and whose filename includes `eventlet`.

    Every other unraisable is forwarded to the default hook.
    """
    if isinstance(unraisable.exc_value, AssertionError):
        traceback_frame_node = unraisable.exc_traceback
        while traceback_frame_node is not None:
            traceback_frame_code = traceback_frame_node.tb_frame.f_code
            is_eventlet_make_thread_handle = (
                traceback_frame_code.co_name == '_make_thread_handle' and
                'eventlet' in traceback_frame_code.co_filename)
            if is_eventlet_make_thread_handle:
                return
            traceback_frame_node = traceback_frame_node.tb_next
    _default_unraisable_hook(unraisable)


def apply():
    """Install the silencing unraisable hook."""
    sys.unraisablehook = _silencing_unraisable_hook
