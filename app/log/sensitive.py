import logging


class Logger(logging.getLoggerClass()):
    """A logger with additional methods for flagging log data as sensitive.

    Use these sensitive log methods whenever the log message might contain
    security-related information (even if it’s just fragments), such as secrets,
    personal data, or anything else that a user likely doesn’t want to be
    revealed when sharing the logs for troubleshooting purposes.
    """

    def __init__(self, name):
        super().__init__(name)

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
