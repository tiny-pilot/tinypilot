import logging

CRITICAL = logging.CRITICAL + 1
ERROR = logging.ERROR + 1
WARNING = logging.WARNING + 1
INFO = logging.INFO + 1
DEBUG = logging.DEBUG + 1

_SENSITIVE_MARKER = '[SENSITIVE]'


def register_levels():
    logging.addLevelName(CRITICAL, 'CRITICAL ' + _SENSITIVE_MARKER)
    logging.addLevelName(ERROR, 'ERROR ' + _SENSITIVE_MARKER)
    logging.addLevelName(WARNING, 'WARNING ' + _SENSITIVE_MARKER)
    logging.addLevelName(INFO, 'INFO ' + _SENSITIVE_MARKER)
    logging.addLevelName(DEBUG, 'DEBUG ' + _SENSITIVE_MARKER)
