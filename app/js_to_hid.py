import dataclasses


@dataclasses.dataclass
class JavaScriptKeyEvent:
    alt_key: bool
    shift_key: bool
    ctrl_key: bool
    key: str
    key_code: int

# JS keycodes source: https://github.com/wesbos/keycodes
# HID keycodes source: https://gist.github.com/MightyPork/6da26e382a7ad91b5496ee55fdc73db2

_JS_TO_HID_KEYCODES = {
  3: 'break',
  8: 0x2a, # Backspace / Delete
  9: 0x2b, # Tab
  12: 0x53, # Clear
  13: 0x29, # Enter
  # HID has support for left and right control keys, but JS does not, so we
  # map all JS control keys to left versions of HID key codes.
  16: 0xe1, # Shift (Left)
  17: 0xe0, # Ctrl (left)
  18: 0xe1, # Alt (left)
  19: 0x48, # Pause/Break
  20: 0x39, # Caps Lock
  21: 0x90, # Hangeul
  25: 0x91, # Hanja
  27: 0x29, # Escape
  32: 0x2c, # Spacebar
  33: 0x4b, # Page Up
  34: 0x4e, # Page Down
  35: 0x4d, # End
  36: 0x41, # Home
  37: 0x50, # Left Arrow
  38: 0x52, # Up Arrow
  39: 0x4f, # Right Arrow
  40: 0x51, # Down Arrow
  41: 0x77, # Select
  43: 0x74, # Execute
  44: 0x46, # Print Screen
  45: 'insert',
  46: 0x4c, # Delete
  47: 0x75, # Help
  48: 0x27, # 0
  49: 0x1e, # 1
  50: 0x1f, # 2
  51: 0x20, # 3
  52: 0x21, # 4
  53: 0x22, # 5
  54: 0x23, # 6
  55: 0x24, # 7
  56: 0x25, # 8
  57: 0x26, # 9
  58: ':',
  59: 0x53, # TODO: 'semicolon (firefox), equals',
  60: 0xc5, # <
  61: 'equals (firefox)',
  63: 'ß',
  64: '@ (firefox)',
  65: 0x04, # a
  66: 0x05, # b
  67: 0x06, # c
  68: 0x07, # d
  69: 0x08, # e
  70: 0x09, # f
  71: 0x0a, # g
  72: 0x0b, # h
  73: 0x0c, # i
  74: 0x0d, # j
  75: 0x0e, # k
  76: 0x0f, # l
  77: 0x10, # m
  78: 0x11, # n
  79: 0x12, # o
  80: 0x13, # p
  81: 0x14, # q
  82: 0x15, # r
  83: 0x16, # s
  84: 0x17, # t
  85: 0x18, # u
  86: 0x19, # v
  87: 0x1a, # w
  88: 0x1b, # x
  89: 0x1c, # y
  90: 0x1d, # z
  91: 'Windows Key / Left ⌘ / Chromebook Search key',
  92: 'right window key',
  93: 'Windows Menu / Right ⌘',
  95: 'sleep',
  96: 'numpad 0',
  97: 'numpad 1',
  98: 'numpad 2',
  99: 'numpad 3',
  100: 'numpad 4',
  101: 'numpad 5',
  102: 'numpad 6',
  103: 'numpad 7',
  104: 'numpad 8',
  105: 'numpad 9',
  106: 'multiply',
  107: 'add',
  108: 'numpad period (firefox)',
  109: 'subtract',
  110: 'decimal point',
  111: 'divide',
  112: 0x3b, # F1
  113: 0x3c, # F2
  114: 0x3d, # F3
  115: 0x3e, # F4
  116: 0x3f, # F5
  117: 0x40, # F6
  118: 0x41, # F7
  119: 0x42, # F8
  120: 0x43, # F9
  121: 0x44, # F10
  122: 0x45, # F11
  123: 0x46, # F12
  124: 0x68, # F13
  125: 0x69, # F14
  126: 0x6a, # F15
  127: 0x6b, # F16
  128: 0x6c, # F17
  129: 0x6d, # F18
  130: 0x6e, # F19
  131: 0x6f, # F20
  132: 0x70, # F21
  133: 0x71, # F22
  134: 0x72, # F23
  144: 'num lock',
  145: 'scroll lock',
  151: 'airplane mode',
  160: '^',
  161: 0x1e, # !
  162: '؛ (arabic semicolon)',
  163: '#',
  164: '$',
  165: 'ù',
  166: 'page backward',
  167: 'page forward',
  168: 'refresh',
  169: 'closing paren (AZERTY)',
  170: '*',
  171: '~ + * key',
  172: 'home key',
  173: 'minus (firefox), mute/unmute',
  174: 'decrease volume level',
  175: 'increase volume level',
  176: 'next',
  177: 'previous',
  178: 'stop',
  179: 'play/pause',
  180: 'e-mail',
  181: 'mute/unmute (firefox)',
  182: 'decrease volume level (firefox)',
  183: 'increase volume level (firefox)',
  186: 'semi-colon / ñ',
  187: 'equal sign',
  188: 'comma',
  189: 'dash',
  190: 'period',
  191: 'forward slash / ç',
  192: 'grave accent / ñ / æ / ö',
  193: '?, / or °',
  194: 'numpad period (chrome)',
  219: 'open bracket',
  220: 'back slash',
  221: 'close bracket / å',
  222: 'single quote / ø / ä',
  223: '`',
  224: 'left or right ⌘ key (firefox)',
  225: 'altgr',
  226: '< /git >, left back slash',
  230: 'GNOME Compose Key',
  231: 'ç',
  233: 'XF86Forward',
  234: 'XF86Back',
  235: 'non-conversion',
  240: 'alphanumeric',
  242: 'hiragana/katakana',
  243: 'half-width/full-width',
  244: 'kanji',
  251: 'unlock trackpad (Chrome/Edge)',
  255: 'toggle touchpad',
}

def convert(js_key_event):
  control_chars = 0
  for i, pressed in enumerate([js_key_event.ctrl_key, js_key_event.shift_key, js_key_event.alt_key]):
    if pressed:
      control_chars |= 1 << i
  # TODO: Handle missing keys
  return control_chars, _JS_TO_HID_KEYCODES[js_key_event.key_code]