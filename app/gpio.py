import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
_OUTPUT_PINS = set()


def turn_pin_on(pin):
    _ensure_pin_is_output(pin)
    GPIO.output(pin, GPIO.HIGH)


def turn_pin_off(pin):
    _ensure_pin_is_output(pin)
    GPIO.output(pin, GPIO.LOW)


def _ensure_pin_is_output(pin):
    """Adds pin to output pin set if it is not already in it."""
    if pin in _OUTPUT_PINS:
        return
    GPIO.setup(pin, GPIO.OUT)
    _OUTPUT_PINS.add(pin)
