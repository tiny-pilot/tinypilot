import dataclasses


class Error(Exception):
    pass


class InvalidButtonState(Error):
    pass


class InvalidRelativePosition(Error):
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


def parse_mouse_event(message):
    return MouseEvent(
        buttons=_parse_button_state(message['buttons']),
        relative_x=_parse_relative_position(message['relativeX']),
        relative_y=_parse_relative_position(message['relativeY']),
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
    if type(relative_position) is not float:
        raise InvalidRelativePosition(
            'Relative position must be a float between 0.0 and 1.0: %s' %
            relative_position)
    if not (0.0 <= relative_position <= 1.0):
        raise InvalidRelativePosition(
            'Relative position must be a float between 0.0 and 1.0: %s' %
            relative_position)
    return relative_position
