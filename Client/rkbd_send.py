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
    "stroke": 0x06,
}


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
            "(print, println, press, release, release_all, stroke) "
            "o un entero (ej: 1 o 0x01)"
        ) from exc

    if not 1 <= value <= 6:
        raise ValueError("El comando debe estar entre 1 y 6")

    return value


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
            "Comando: print|println|press|release|release_all|stroke "
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
    command_byte = bytes([parse_command(command_name)])

    if is_hex:
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