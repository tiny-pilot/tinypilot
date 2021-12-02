"""Contains the configuration for our custom logging setup.

This module must be the first of the local imports in the file that contains the
`main` function. It overrides the default logger class, so that a call to
`logging.getLogger(__name__)` returns an instance of `_SensitiveLogger`.
"""
import logging


def create_root_logger(handler):
    """Creates a pre-configured root logger.

    The logger is set up with custom formatting, and the provided handler is
    attached to it. Note that importing this package has a side-effect, which
    is described in the `__init__.py` file.

    Args:
        handler: The log handler that shall be used (type `logging.Handler`).

    Returns:
        A logger object of type `logging.Logger`.
    """
    handler.setFormatter(
        logging.Formatter(
            '%(asctime)s.%(msecs)03d %(name)-15s %(levelname)-4s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'))

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    return root_logger


class _SensitiveLogger(logging.getLoggerClass()):
    """A logger with additional methods for flagging log data as sensitive.

    Use these sensitive log methods whenever the log message might contain
    security-related information (even if it’s just fragments), such as secrets,
    personal data, or anything else that a user likely doesn’t want to be
    revealed when sharing the logs for troubleshooting purposes.
    """

    def log_sensitive(self, level, message, *args, **kws):
        if self.isEnabledFor(level):
            # Since we do string concatenation here, we cast the message to
            # string explicitly, just to avoid potential type errors if someone
            # passes an Error object for example.
            # The closing marker is needed, because a log message might contain
            # newlines. Otherwise, we wouldn’t be able to tell in hindsight how
            # many lines a log message consists of.
            self._log(level, '[SENSITIVE] ' + str(message) + ' [/SENSITIVE]',
                      args, **kws)

    def debug_sensitive(self, message, *args, **kws):
        self.log_sensitive(logging.DEBUG, message, *args, **kws)

    def info_sensitive(self, message, *args, **kws):
        self.log_sensitive(logging.INFO, message, *args, **kws)

    def warning_sensitive(self, message, *args, **kws):
        self.log_sensitive(logging.WARNING, message, *args, **kws)

    def error_sensitive(self, message, *args, **kws):
        self.log_sensitive(logging.ERROR, message, *args, **kws)

    def exception_sensitive(self, message, *args, **kws):
        self.log_sensitive(logging.ERROR, message, *args, exc_info=True, **kws)


logging.setLoggerClass(_SensitiveLogger)
