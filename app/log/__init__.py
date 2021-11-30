import logging

import log.sensitive

# Override the default logger class, so that it uses `sensitive.Logger`
# everywhere we say `logging.getLogger(...)`.
logging.setLoggerClass(log.sensitive.Logger)
