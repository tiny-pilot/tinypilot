import eventlet


def reschedule(seconds=0):
    """Reschedules the current thread to allow other waiting threads to proceed.

    When carrying out longer-running operations e.g. in a while loop, the Python
    process is blocked by default. That means that all other threads are frozen.
    This problem can be avoided by frequently calling this method in the loop at
    a (most likely) negligible performance penalty.

    Args:
        seconds: An integer or a float of the number of seconds to yield for.
    """
    # Flask uses eventlet internally. Calling `time.sleep` wouldn’t help here,
    # since we don’t (and don’t want to) monkey-patch Python’s time API.
    eventlet.sleep(seconds)
