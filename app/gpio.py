import os

# pylint: disable=no-member
# pylint: disable=import-error

if 'DEBUG' in os.environ:
    import mock_gpio as GPIO
else:
    import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
_OUTPUT_PINS = set()


class Error(Exception):
    pass


def turn_pin_on(pin):
    _ensure_pin_is_output(pin)
    try:
        GPIO.output(pin, GPIO.HIGH)
    except Exception as e:
        raise Error(e) from e


def turn_pin_off(pin):
    _ensure_pin_is_output(pin)
    try:
        GPIO.output(pin, GPIO.LOW)
    except Exception as e:
        raise Error(e.message) from e


def cleanup():
    for pin in _OUTPUT_PINS:
        turn_pin_off(pin)
    GPIO.cleanup()


def _ensure_pin_is_output(pin):
    """Adds pin to output pin set if it is not already in it."""
    if pin in _OUTPUT_PINS:
        return
    GPIO.setup(pin, GPIO.OUT)
    _OUTPUT_PINS.add(pin)
