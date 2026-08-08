KEYS = {
    # Teclas modificadoras
    "KEY_LEFT_CTRL": 0x80,
    "KEY_LEFT_SHIFT": 0x81,
    "KEY_LEFT_ALT": 0x82,
    "KEY_LEFT_GUI": 0x83,
    "KEY_RIGHT_CTRL": 0x84,
    "KEY_RIGHT_SHIFT": 0x85,
    "KEY_RIGHT_ALT": 0x86,
    "KEY_RIGHT_GUI": 0x87,

    # Usamos las teclas de la izquierda si no se especifica un lado
    "KEY_CTRL": 0x80,
    "KEY_SHIFT": 0x81,
    "KEY_ALT": 0x82,
    "KEY_GUI": 0x83,

    # Teclas de navegacion y sistema
    "KEY_UP_ARROW": 0xDA,
    "KEY_DOWN_ARROW": 0xD9,
    "KEY_LEFT_ARROW": 0xD8,
    "KEY_RIGHT_ARROW": 0xD7,
    "KEY_MENU": 0xED,
    "KEY_SPACE": 0x20,
    "KEY_BACKSPACE": 0xB2,
    "KEY_TAB": 0xB3,
    "KEY_RETURN": 0xB0,
    "KEY_ESC": 0xB1,
    "KEY_INSERT": 0xD1,
    "KEY_DELETE": 0xD4,
    "KEY_PAGE_UP": 0xD3,
    "KEY_PAGE_DOWN": 0xD6,
    "KEY_HOME": 0xD2,
    "KEY_END": 0xD5,
    "KEY_NUM_LOCK": 0xDB,
    "KEY_CAPS_LOCK": 0xC1,

    # Teclas de funcion
    "KEY_F1": 0xC2,
    "KEY_F2": 0xC3,
    "KEY_F3": 0xC4,
    "KEY_F4": 0xC5,
    "KEY_F5": 0xC6,
    "KEY_F6": 0xC7,
    "KEY_F7": 0xC8,
    "KEY_F8": 0xC9,
    "KEY_F9": 0xCA,
    "KEY_F10": 0xCB,
    "KEY_F11": 0xCC,
    "KEY_F12": 0xCD,
    "KEY_F13": 0xF0,
    "KEY_F14": 0xF1,
    "KEY_F15": 0xF2,
    "KEY_F16": 0xF3,
    "KEY_F17": 0xF4,
    "KEY_F18": 0xF5,
    "KEY_F19": 0xF6,
    "KEY_F20": 0xF7,
    "KEY_F21": 0xF8,
    "KEY_F22": 0xF9,
    "KEY_F23": 0xFA,
    "KEY_F24": 0xFB,

    "KEY_PRINT_SCREEN": 0xCE,
    "KEY_SCROLL_LOCK": 0xCF,
    "KEY_PAUSE": 0xD0,

    # Numeric keypad
    "KEY_KP_SLASH": 0xDC,
    "KEY_KP_ASTERISK": 0xDD,
    "KEY_KP_MINUS": 0xDE,
    "KEY_KP_PLUS": 0xDF,
    "KEY_KP_ENTER": 0xE0,
    "KEY_KP_1": 0xE1,
    "KEY_KP_2": 0xE2,
    "KEY_KP_3": 0xE3,
    "KEY_KP_4": 0xE4,
    "KEY_KP_5": 0xE5,
    "KEY_KP_6": 0xE6,
    "KEY_KP_7": 0xE7,
    "KEY_KP_8": 0xE8,
    "KEY_KP_9": 0xE9,
    "KEY_KP_0": 0xEA,
    "KEY_KP_DOT": 0xEB,
}


CONSUMER_CONTROL = {
    # Power Control
    "POWER": 0x0030,
    "RESET": 0x0031,
    "SLEEP": 0x0032,

    # Screen Brightness
    "BRIGHTNESS_INCREMENT": 0x006F,
    "BRIGHTNESS_DECREMENT": 0x0070,

    # Wireless Radio Controls
    "WIRELESS_RADIO_CONTROLS": 0x000C,
    "WIRELESS_RADIO_BUTTONS": 0x00C6,
    "WIRELESS_RADIO_LED": 0x00C7,
    "WIRELESS_RADIO_SLIDER_SWITCH": 0x00C8,

    # Media Control
    "RECORD": 0x00B2,
    "FAST_FORWARD": 0x00B3,
    "REWIND": 0x00B4,
    "SCAN_NEXT": 0x00B5,
    "SCAN_PREVIOUS": 0x00B6,
    "STOP": 0x00B7,
    "EJECT": 0x00B8,
    "PLAY_PAUSE": 0x00CD,
    "VOLUME": 0x00E0,
    "MUTE": 0x00E2,
    "BASS": 0x00E3,
    "TREBLE": 0x00E4,
    "BASS_BOOST": 0x00E5,
    "VOLUME_INCREMENT": 0x00E9,
    "VOLUME_DECREMENT": 0x00EA,
    "BASS_INCREMENT": 0x0152,
    "BASS_DECREMENT": 0x0153,
    "TREBLE_INCREMENT": 0x0154,
    "TREBLE_DECREMENT": 0x0155,

    # Application Launcher
    "CONFIGURATION": 0x0183,
    "EMAIL_READER": 0x018A,
    "CALCULATOR": 0x0192,
    "LOCAL_BROWSER": 0x0194,

    # Browser/Explorer Specific
    "SEARCH": 0x0221,
    "HOME": 0x0223,
    "BACK": 0x0224,
    "FORWARD": 0x0225,
    "BR_STOP": 0x0226,
    "REFRESH": 0x0227,
    "BOOKMARKS": 0x022A,
}

SYSTEM_CONTROL = {
    "POWER_DOWN": 0x01,
    "SLEEP": 0x02,
    "WAKE_UP": 0x03,
}