import logging


class Logger(logging.getLoggerClass()):
    """A logger with additional methods for flagging log data as sensitive.

    Use these sensitive log messages whenever the log message might contain
    security-related information (even if it’s just fragments), such as secrets,
    personal data, or anything else that a user likely doesn’t want to be
    revealed when sharing the logs for trouble-shooting purposes.
    """

    def __init__(self, name):
        logging.Logger.__init__(self, name)

    def log_sensitive(self, level, message, *args, **kws):
        if self.isEnabledFor(level):
            # Since we do string concatenation here, we cast the message to
            # string explicitly, just to avoid potential type errors if someone
            # passes an Error object for example.
            # pylint: disable=protected-access
            self._log(level, '[SENSITIVE] ' + str(message), args, **kws)

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
