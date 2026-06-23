#!/usr/bin/env python3

import sys
import os
import hmac
import hashlib
import struct
import time
import argparse
import getpass
from dotenv import load_dotenv

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import paho.mqtt.client as mqtt

load_dotenv()

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "rkbd")
MQTT_USER = os.getenv("MQTT_USER", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")

AES_KEY = bytes.fromhex(os.getenv("AES_KEY", ""))
HMAC_KEY = bytes.fromhex(os.getenv("HMAC_KEY", ""))

COMMANDS = {
    "print": 0x01,
    "println": 0x02,
    "press": 0x03,
    "release": 0x04,
    "release_all": 0x05,
    "release-all": 0x05,
    "releaseall": 0x05,
    "hotkey": 0x06
}


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

    # Teclas de navegación y sistema
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

    # Teclas de función
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

# Índices inversos para búsquedas rápidas
_KEYS_UPPER = {k.upper(): v for k, v in KEYS.items()}
_KEYS_NO_PREFIX = {k.replace("KEY_", "").upper(): v for k, v in KEYS.items()}

def encrypt_payload(counter_bytes: bytes, random_bytes: bytes, payload: bytes) -> bytes:
    nonce = counter_bytes + random_bytes

    cipher = Cipher(
        algorithms.AES(AES_KEY),
        modes.CTR(nonce)
    )

    encryptor = cipher.encryptor()
    return encryptor.update(payload) + encryptor.finalize()


def build_message(command: bytes) -> bytes:
    if len(command) > 16:
        raise ValueError("El comando no puede tener más de 16 bytes")

    counter = int(time.time_ns() / 1000)

    counter_bytes = struct.pack(">Q", counter)
    random_bytes = os.urandom(8)

    payload = command.ljust(16, b"\x00")

    ciphertext = encrypt_payload(
        counter_bytes,
        random_bytes,
        payload
    )

    data_to_auth = counter_bytes + random_bytes + ciphertext

    tag = hmac.new(
        HMAC_KEY,
        data_to_auth,
        hashlib.sha256
    ).digest()

    return data_to_auth + tag


def parse_command(command_name: str) -> int:
    command_name = command_name.lower()
    if command_name in COMMANDS:
        return COMMANDS[command_name]

    try:
        if command_name.startswith("0x"):
            value = int(command_name, 16)
        else:
            value = int(command_name)
    except ValueError as exc:
        raise ValueError(
            "El comando debe ser un nombre valido "
            "(print, println, press, release, release_all, hotkey) "
            "o un entero (ej: 1 o 0x01)"
        ) from exc

    if not 1 <= value <= 6:
        raise ValueError("El comando debe estar entre 1 y 6")

    return value

def parse_hotkey(hotkey: str) -> bytes:
    if not hotkey or not hotkey.strip():
        raise ValueError("El hotkey no puede estar vacío")

    keys = [key.strip() for key in hotkey.split("+") if key.strip()]
    if not keys:
        raise ValueError("Formato de hotkey inválido")

    key_bytes: list[int] = []
    for key in keys:
        key_upper = key.upper()

        # Si es una letra simple (A-Z), usamos su byte ASCII.
        if len(key) == 1 and key.isalpha() and "A" <= key_upper <= "Z":
            key_bytes.append(ord(key_upper))
            continue

        # Buscar en índices inversos
        matched_code = _KEYS_UPPER.get(key_upper) or _KEYS_NO_PREFIX.get(key_upper)
        
        if matched_code is None:
            raise ValueError(f"Tecla desconocida en hotkey: '{key}'")

        key_bytes.append(matched_code)

    return bytes(key_bytes)
        
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Envia comandos cifrados a un teclado remoto"
    )
    parser.add_argument(
        "--hex",
        action="store_true",
        help="Interpreta 'data' como cadena hexadecimal"
    )
    parser.add_argument(
        "-p",
        "--password",
        action="store_true",
        help="Lee 'data' desde stdin sin eco (util para contraseñas)"
    )
    parser.add_argument(
        "command",
        help=(
            "Comando: print|println|press|release|release_all|hotkey "
            "(o 1-6 en decimal/0xNN)"
        )
    )
    parser.add_argument(
        "data",
        nargs="?",
        help="Parámetros del comando (texto normal o hex si se usa --hex)"
    )
    args = parser.parse_args()

    if args.password and args.data is not None:
        parser.error("No pases 'data' como argumento si usas --password")

    if not args.password and args.data is None:
        parser.error("Falta el argumento 'data' (o usa --password)")

    return args


def read_data_from_stdin() -> str:
    if sys.stdin.isatty():
        return getpass.getpass(prompt="")
    return sys.stdin.read().rstrip("\r\n")


def build_command_bytes(command_name: str, data: str, is_hex: bool) -> bytes:
    command_code = parse_command(command_name)
    command_byte = bytes([command_code])

    if command_code == COMMANDS["hotkey"]:
        data_bytes = parse_hotkey(data)
    elif is_hex:
        data_bytes = bytes.fromhex(data)
    else:
        data_bytes = data.encode("utf-8")

    command = command_byte + data_bytes
    if len(command) > 16:
        raise ValueError("El comando (tipo + datos) no puede superar 16 bytes")

    return command


def main():
    args = parse_args()
    data = read_data_from_stdin() if args.password else args.data

    try:
        command = build_command_bytes(
            args.command,
            data,
            args.hex
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    message = build_message(command)

    print("Mensaje hex:")
    print(message.hex().upper())

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )
    if MQTT_USER and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.connect(MQTT_HOST, MQTT_PORT, 60)

    client.publish(
        MQTT_TOPIC,
        payload=message,
        qos=0,
        retain=False
    ).wait_for_publish()

    client.disconnect()

    print("Mensaje enviado")


if __name__ == "__main__":
    main()