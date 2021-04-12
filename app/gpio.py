import datetime
import os
import time

# pylint: disable=no-member
# pylint: disable=import-error

if 'DEBUG' in os.environ:
    import mock_gpio as GPIO
else:
    import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
_OUTPUT_PINS = set()

# Hacky way to ensure that we don't turn the pin off and on so fast that it has
# no effect.
_MIN_PIN_ON_MILLISECONDS = 100
# Mapping of pin to the earliest datetime it can be turned off.
_EARLIEST_PIN_OFF_TIME = {}


class Error(Exception):
    pass


def turn_pin_on(pin):
    _ensure_pin_is_output(pin)
    try:
        GPIO.output(pin, GPIO.HIGH)
    except Exception as e:
        raise Error(e) from e
    _EARLIEST_PIN_OFF_TIME[pin] = (
        datetime.datetime.now() +
        datetime.timedelta(milliseconds=_MIN_PIN_ON_MILLISECONDS))


def turn_pin_off(pin):
    _ensure_pin_is_output(pin)
    _wait_for_earliest_pin_off_time(pin)
    try:
        GPIO.output(pin, GPIO.LOW)
    except Exception as e:
        raise Error(e.message) from e


def cleanup():
    # Reset limits on turning pins off.
    # pylint: disable=global-statement
    global _EARLIEST_PIN_OFF_TIME
    _EARLIEST_PIN_OFF_TIME = {}

    for pin in _OUTPUT_PINS:
        turn_pin_off(pin)
    GPIO.cleanup()


def _ensure_pin_is_output(pin):
    """Adds pin to output pin set if it is not already in it."""
    if pin in _OUTPUT_PINS:
        return
    GPIO.setup(pin, GPIO.OUT)
    _OUTPUT_PINS.add(pin)


def _wait_for_earliest_pin_off_time(pin):
    now = datetime.datetime.now()
    off_time = _EARLIEST_PIN_OFF_TIME.get(pin, now)
    sleep_seconds = (off_time - now).total_seconds()
    if sleep_seconds <= 0:
        return
    time.sleep(sleep_seconds)
