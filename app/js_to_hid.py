from hid import keycodes as hid


class Error(Exception):
    pass


class UnrecognizedKeyCodeError(Error):
    pass


_MODIFIER_KEYCODES = [
    'AltLeft',
    'AltRight',
    'ControlLeft',
    'ControlRight',
    'MetaLeft',
    'MetaRight',
    'ShiftLeft',
    'ShiftRight',
]

_MAPPING = {
    'AltLeft': hid.KEYCODE_LEFT_ALT,
    'AltRight': hid.KEYCODE_RIGHT_ALT,
    'ArrowDown': hid.KEYCODE_DOWN_ARROW,
    'ArrowLeft': hid.KEYCODE_LEFT_ARROW,
    'ArrowRight': hid.KEYCODE_RIGHT_ARROW,
    'ArrowUp': hid.KEYCODE_UP_ARROW,
    'Backquote': hid.KEYCODE_ACCENT_GRAVE,
    'Backslash': hid.KEYCODE_BACKSLASH,
    'Backspace': hid.KEYCODE_BACKSPACE_DELETE,
    'BracketLeft': hid.KEYCODE_LEFT_BRACKET,
    'BracketRight': hid.KEYCODE_RIGHT_BRACKET,
    'CapsLock': hid.KEYCODE_CAPS_LOCK,
    'Comma': hid.KEYCODE_COMMA,
    'ContextMenu': hid.KEYCODE_CONTEXT_MENU,
    'ControlLeft': hid.KEYCODE_LEFT_CTRL,
    'ControlRight': hid.KEYCODE_RIGHT_CTRL,
    'Delete': hid.KEYCODE_DELETE,
    'Digit0': hid.KEYCODE_NUMBER_0,
    'Digit1': hid.KEYCODE_NUMBER_1,
    'Digit2': hid.KEYCODE_NUMBER_2,
    'Digit3': hid.KEYCODE_NUMBER_3,
    'Digit4': hid.KEYCODE_NUMBER_4,
    'Digit5': hid.KEYCODE_NUMBER_5,
    'Digit6': hid.KEYCODE_NUMBER_6,
    'Digit7': hid.KEYCODE_NUMBER_7,
    'Digit8': hid.KEYCODE_NUMBER_8,
    'Digit9': hid.KEYCODE_NUMBER_9,
    'End': hid.KEYCODE_END,
    'Enter': hid.KEYCODE_ENTER,
    'Equal': hid.KEYCODE_EQUAL_SIGN,
    'Escape': hid.KEYCODE_ESCAPE,
    'F1': hid.KEYCODE_F1,
    'F2': hid.KEYCODE_F2,
    'F3': hid.KEYCODE_F3,
    'F4': hid.KEYCODE_F4,
    'F5': hid.KEYCODE_F5,
    'F6': hid.KEYCODE_F6,
    'F7': hid.KEYCODE_F7,
    'F8': hid.KEYCODE_F8,
    'F9': hid.KEYCODE_F9,
    'F10': hid.KEYCODE_F10,
    'F11': hid.KEYCODE_F11,
    'F12': hid.KEYCODE_F12,
    'F13': hid.KEYCODE_F13,
    'F14': hid.KEYCODE_F14,
    'F15': hid.KEYCODE_F15,
    'F16': hid.KEYCODE_F16,
    'F17': hid.KEYCODE_F17,
    'F18': hid.KEYCODE_F18,
    'F19': hid.KEYCODE_F19,
    'F20': hid.KEYCODE_F20,
    'F21': hid.KEYCODE_F21,
    'F22': hid.KEYCODE_F22,
    'F23': hid.KEYCODE_F23,
    'Home': hid.KEYCODE_HOME,
    'Insert': hid.KEYCODE_INSERT,
    'IntlBackslash': hid.KEYCODE_102ND,
    'IntlRo': hid.KEYCODE_INTL_RO,
    'IntlYen': hid.KEYCODE_INTL_YEN,
    'KeyA': hid.KEYCODE_A,
    'KeyB': hid.KEYCODE_B,
    'KeyC': hid.KEYCODE_C,
    'KeyD': hid.KEYCODE_D,
    'KeyE': hid.KEYCODE_E,
    'KeyF': hid.KEYCODE_F,
    'KeyG': hid.KEYCODE_G,
    'KeyH': hid.KEYCODE_H,
    'KeyI': hid.KEYCODE_I,
    'KeyJ': hid.KEYCODE_J,
    'KeyK': hid.KEYCODE_K,
    'KeyL': hid.KEYCODE_L,
    'KeyM': hid.KEYCODE_M,
    'KeyN': hid.KEYCODE_N,
    'KeyO': hid.KEYCODE_O,
    'KeyP': hid.KEYCODE_P,
    'KeyQ': hid.KEYCODE_Q,
    'KeyR': hid.KEYCODE_R,
    'KeyS': hid.KEYCODE_S,
    'KeyT': hid.KEYCODE_T,
    'KeyU': hid.KEYCODE_U,
    'KeyV': hid.KEYCODE_V,
    'KeyW': hid.KEYCODE_W,
    'KeyX': hid.KEYCODE_X,
    'KeyY': hid.KEYCODE_Y,
    'KeyZ': hid.KEYCODE_Z,
    'MetaLeft': hid.KEYCODE_LEFT_META,
    'MetaRight': hid.KEYCODE_RIGHT_META,
    'Minus': hid.KEYCODE_MINUS,
    'Numpad0': hid.KEYCODE_NUMPAD_0,
    'Numpad1': hid.KEYCODE_NUMPAD_1,
    'Numpad2': hid.KEYCODE_NUMPAD_2,
    'Numpad3': hid.KEYCODE_NUMPAD_3,
    'Numpad4': hid.KEYCODE_NUMPAD_4,
    'Numpad5': hid.KEYCODE_NUMPAD_5,
    'Numpad6': hid.KEYCODE_NUMPAD_6,
    'Numpad7': hid.KEYCODE_NUMPAD_7,
    'Numpad8': hid.KEYCODE_NUMPAD_8,
    'Numpad9': hid.KEYCODE_NUMPAD_9,
    'NumpadMultiply': hid.KEYCODE_NUMPAD_MULTIPLY,
    'NumpadAdd': hid.KEYCODE_NUMPAD_PLUS,
    'NumpadSubtract': hid.KEYCODE_NUMPAD_MINUS,
    'NumpadDecimal': hid.KEYCODE_NUMPAD_DOT,
    'NumpadDivide': hid.KEYCODE_NUMPAD_DIVIDE,
    'NumpadEnter': hid.KEYCODE_NUMPAD_ENTER,
    'NumLock': hid.KEYCODE_NUM_LOCK,
    'OSLeft': hid.KEYCODE_LEFT_META,
    'OSRight': hid.KEYCODE_RIGHT_META,
    'PageUp': hid.KEYCODE_PAGE_UP,
    'PageDown': hid.KEYCODE_PAGE_DOWN,
    'Pause': hid.KEYCODE_PAUSE_BREAK,
    'Period': hid.KEYCODE_PERIOD,
    'PrintScreen': hid.KEYCODE_PRINT_SCREEN,
    'Quote': hid.KEYCODE_SINGLE_QUOTE,
    'ScrollLock': hid.KEYCODE_SCROLL_LOCK,
    'Select': hid.KEYCODE_SELECT,
    'Semicolon': hid.KEYCODE_SEMICOLON,
    'ShiftLeft': hid.KEYCODE_LEFT_SHIFT,
    'ShiftRight': hid.KEYCODE_RIGHT_SHIFT,
    'Space': hid.KEYCODE_SPACEBAR,
    'Slash': hid.KEYCODE_FORWARD_SLASH,
    'Tab': hid.KEYCODE_TAB,
}


def convert(keystroke):
    return hid.Keystroke(keycode=_map_keycode(keystroke),
                         modifier=_map_modifier_keys(keystroke))


def _map_modifier_keys(keystroke):
    modifier_bitmask = 0

    if keystroke.left_ctrl_modifier:
        modifier_bitmask |= hid.MODIFIER_LEFT_CTRL
    if keystroke.right_ctrl_modifier:
        modifier_bitmask |= hid.MODIFIER_RIGHT_CTRL

    if keystroke.left_shift_modifier:
        modifier_bitmask |= hid.MODIFIER_LEFT_SHIFT
    if keystroke.right_shift_modifier:
        modifier_bitmask |= hid.MODIFIER_RIGHT_SHIFT

    if keystroke.left_alt_modifier:
        modifier_bitmask |= hid.MODIFIER_LEFT_ALT
    if keystroke.right_alt_modifier:
        modifier_bitmask |= hid.MODIFIER_RIGHT_ALT

    if keystroke.left_meta_modifier:
        modifier_bitmask |= hid.MODIFIER_LEFT_META
    if keystroke.right_meta_modifier:
        modifier_bitmask |= hid.MODIFIER_RIGHT_META

    return modifier_bitmask


def _map_keycode(keystroke):
    # If the current key press is a modifier key and it's the *only* modifier
    # being pressed, treat it as a special case where we remap the HID code to
    # KEYCODE_NONE. This is based on a report that certain KVMs only recognize
    # a modifier keystroke if the HID code is KEYCODE_NONE, but we should verify
    # that it matches behavior from normal USB keyboards.
    if (keystroke.code in _MODIFIER_KEYCODES and
            _count_modifiers(keystroke) == 1):
        return hid.KEYCODE_NONE

    try:
        return _MAPPING[keystroke.code]
    except KeyError as e:
        raise UnrecognizedKeyCodeError(
            f'Unrecognized key code {keystroke.key} {keystroke.code}') from e


def _count_modifiers(keystroke):
    return (int(keystroke.left_ctrl_modifier) +
            int(keystroke.right_ctrl_modifier) +
            int(keystroke.left_shift_modifier) +
            int(keystroke.right_shift_modifier) +
            int(keystroke.left_alt_modifier) +
            int(keystroke.right_alt_modifier) +
            int(keystroke.left_meta_modifier) +
            int(keystroke.right_meta_modifier))
