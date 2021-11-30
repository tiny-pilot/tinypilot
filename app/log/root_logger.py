import logging


def create(handler):
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
