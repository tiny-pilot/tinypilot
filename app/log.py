import logging


class SensitiveLogger(logging.getLoggerClass()):
    """Provides additional log methods for logging out sensitive data.
    """

    def __init__(self, name):
        logging.Logger.__init__(self, name)

    def log_sensitive(self, level, message, *args, **kws):
        if self.isEnabledFor(level):
            # pylint: disable=protected-access
            self._log(level, '[SENSITIVE] ' + message, args, **kws)

    def debug_sensitive(self, message, *args, **kws):
        self.log_sensitive(logging.DEBUG, message, *args, **kws)

    def info_sensitive(self, message, *args, **kws):
        self.log_sensitive(logging.INFO, message, *args, **kws)

    def warning_sensitive(self, message, *args, **kws):
        self.log_sensitive(logging.WARNING, message, *args, **kws)

    def error_sensitive(self, message, *args, **kws):
        self.log_sensitive(logging.ERROR, message, *args, **kws)
