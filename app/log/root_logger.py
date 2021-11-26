import logging


def create(handler):
    handler.setFormatter(
        logging.Formatter(
            '%(asctime)s.%(msecs)03d %(name)-15s %(levelname)-4s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'))

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    return root_logger
