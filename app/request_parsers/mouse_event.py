import dataclasses


class Error(Exception):
    pass


class MissingField(Error):
    pass


class InvalidButtonState(Error):
    pass


class InvalidRelativePosition(Error):
    pass


class InvalidWheelValue(Error):
    pass


# JavaScript only supports 5 mouse buttons.
# https://developer.mozilla.org/en-US/docs/Web/API/MouseEvent/buttons
_MAX_BUTTONS = 5
_MAX_BUTTON_STATE = pow(2, _MAX_BUTTONS) - 1


@dataclasses.dataclass
class MouseEvent:
    # A bitmask of buttons pressed during the mouse event.
    buttons: int

    # A value from 0.0 to 1.0 representing the cursor's relative position on the
    # screen.
    relative_x: int
    relative_y: int

    # Wheel deltas can either be:
    # -1 - Scroll up.
    #  0 - Don't change scroll position.
    #  1 - Scroll down.
    vertical_wheel_delta: int
    horizontal_wheel_delta: int


def parse_mouse_event(message):
    if not isinstance(message, dict):
        raise MissingField(
            'Mouse event parameter is invalid, expecting a dictionary data type'
        )
    required_fields = ('buttons', 'relativeX', 'relativeY',
                       'verticalWheelDelta', 'horizontalWheelDelta')
    for field in required_fields:
        if field not in message:
            raise MissingField(
                'Mouse event request is missing required field: %s' % field)
    return MouseEvent(
        buttons=_parse_button_state(message['buttons']),
        relative_x=_parse_relative_position(message['relativeX']),
        relative_y=_parse_relative_position(message['relativeY']),
        vertical_wheel_delta=_parse_wheel_value(message['verticalWheelDelta']),
        horizontal_wheel_delta=_parse_wheel_value(
            message['horizontalWheelDelta']),
    )


def _parse_button_state(buttons):
    if type(buttons) is not int:
        raise InvalidButtonState('Button state must be an integer value: %s' %
                                 buttons)
    if not (0 <= buttons <= _MAX_BUTTON_STATE):
        raise InvalidButtonState('Button state must be <= 0x%x: %s' %
                                 (_MAX_BUTTON_STATE, buttons))
    return buttons


def _parse_relative_position(relative_position):
    if type(relative_position) is not float and type(
            relative_position) is not int:
        raise InvalidRelativePosition(
            'Relative position must be a float between 0.0 and 1.0: %s' %
            relative_position)
    if not (0.0 <= relative_position <= 1.0):
        raise InvalidRelativePosition(
            'Relative position must be a float between 0.0 and 1.0: %s' %
            relative_position)
    return relative_position


def _parse_wheel_value(wheel_value):
    if type(wheel_value) is not int:
        raise InvalidWheelValue('Wheel value must be a int: %s' % wheel_value)
    if wheel_value not in (-1, 0, 1):
        raise InvalidWheelValue('Wheel value must be -1, 0, or 1: %s' %
                                wheel_value)
    return wheel_value
