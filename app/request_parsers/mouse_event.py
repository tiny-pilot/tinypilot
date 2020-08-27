import dataclasses


class Error(Exception):
    pass


class InvalidButtonState(Exception):
    pass


class InvalidRelativePosition(Exception):
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
    buttons = message['buttons']
    if buttons > _MAX_BUTTON_STATE:
        raise InvalidButtonState('Button state must be <= 0x%x: %s' %
                                 (_MAX_BUTTON_STATE, buttons))

    relative_x = message['relativeX']
    if not _validate_relative_position(relative_x):
        raise InvalidRelativePosition(
            'Relative x-position must be between 0.0 and 1.0: %s' % relative_x)
    relative_y = message['relativeY']
    if not _validate_relative_position(relative_y):
        raise InvalidRelativePosition(
            'Relative y-position must be between 0.0 and 1.0: %s' % relative_y)

    return MouseEvent(
        buttons=buttons,
        relative_x=relative_x,
        relative_y=relative_y,
    )


def _validate_relative_position(relative_position):
    return 0.0 <= relative_position <= 1.0
