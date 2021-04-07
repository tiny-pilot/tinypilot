# Mock GPIO module for development. Replaces RPi.GPIO module, which is hard to
# run on non-Pi machines.

import logging

logger = logging.getLogger(__name__)

LOW = 0
HIGH = 1
OUT = 1000
BCM = 100


def setup(pin, pin_type):
    logger.info("gpio.setup(pin=%d, type=%d)", pin, pin_type)


def output(pin, state):
    logger.info("gpio.output(pin=%d, state=%d)", pin, state)


def setmode(mode):
    logger.info("gpio.setmode(mode=%d)", mode)


def cleanup():
    logger.info("gpio.cleanup()")
