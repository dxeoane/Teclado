#!/usr/bin/env python3

import sys
import os
import hmac
import hashlib
import struct
import time
import argparse
import getpass
import ipaddress
from typing import Optional
from dotenv import load_dotenv

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import paho.mqtt.client as mqtt
from hid_codes import KEYS, CONSUMER_CONTROL, SYSTEM_CONTROL

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
    "hotkey": 0x06,
    "wake_on_lan": 0x07,
    "consumer": 0x08,
    "system": 0x09
}

# Índices inversos para búsquedas rápidas
_KEYS_UPPER = {k.upper(): v for k, v in KEYS.items()}
_KEYS_NO_PREFIX = {k.replace("KEY_", "").upper(): v for k, v in KEYS.items()}
_CONSUMER_CONTROL_CODES = {k.upper(): v for k, v in CONSUMER_CONTROL.items()}
_SYSTEM_CONTROL_CODES = {k.upper(): v for k, v in SYSTEM_CONTROL.items()}


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
            "(print, println, press, release, release_all, hotkey, wake_on_lan, consumer, system) "
            "o un entero (ej: 1 o 0x01)"
        ) from exc

    if not 1 <= value <= 9:
        raise ValueError("El comando debe estar entre 1 y 9")

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

def parse_consumer_control(control: str) -> bytes:
    if not control or not control.strip():
        raise ValueError("El código no puede estar vacío")

    control_upper = control.strip().upper()

    # Buscar en índices inversos
    matched_code = _CONSUMER_CONTROL_CODES.get(control_upper)
    
    if matched_code is None:
        raise ValueError(f"Código desconocido: '{control}'")

    return matched_code.to_bytes(2, byteorder="big")

def parse_system_control(control: str) -> bytes:
    if not control or not control.strip():
        raise ValueError("El código no puede estar vacío")

    control_upper = control.strip().upper()

    # Buscar en índices inversos
    matched_code = _SYSTEM_CONTROL_CODES.get(control_upper)
    
    if matched_code is None:
        raise ValueError(f"Código desconocido: '{control}'")

    return bytes([matched_code])
        
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
            "Comando: print|println|press|release|release_all|hotkey|wake_on_lan|consumer|system "
            "(wake_on_lan usa IP de broadcast y MAC separadas; también acepta 1-9 en decimal/0xNN)"
        )
    )
    parser.add_argument(
        "data",
        nargs="?",
        help="Parámetro principal del comando (texto normal o hex si se usa --hex)"
    )
    parser.add_argument(
        "data2",
        nargs="?",
        help="Segundo parámetro para wake_on_lan (MAC en hex)"
    )
    args = parser.parse_args()

    if args.password and args.data is not None:
        parser.error("No pases 'data' como argumento si usas --password")

    if not args.password and args.data is None:
        parser.error("Falta el argumento 'data' (o usa --password)")

    if args.command.lower() == "wake_on_lan":
        if args.data is None or args.data2 is None:
            parser.error(
                "wake_on_lan requiere dos argumentos: IP de broadcast y MAC"
            )
    elif args.data2 is not None:
        parser.error("Este comando solo acepta un argumento de datos")

    return args


def read_data_from_stdin() -> str:
    if sys.stdin.isatty():
        return getpass.getpass(prompt="")
    return sys.stdin.read().rstrip("\r\n")


def build_command_bytes(
    command_name: str,
    data: str,
    is_hex: bool,
    data2: Optional[str] = None,
) -> bytes:
    command_code = parse_command(command_name)
    command_byte = bytes([command_code])

    if command_code == COMMANDS["hotkey"]:
        data_bytes = parse_hotkey(data)
    elif command_code == COMMANDS["consumer"]:
        data_bytes = parse_consumer_control(data)
    elif command_code == COMMANDS["system"]:
        data_bytes = parse_system_control(data)    
    elif command_code == COMMANDS["wake_on_lan"]:
        try:
            broadcast_address = ipaddress.IPv4Address(data)
        except ipaddress.AddressValueError as exc:
            raise ValueError(f"IP de broadcast inválida: '{data}'") from exc

        if data2 is None:
            raise ValueError("wake_on_lan requiere una MAC")

        mac_hex = data2.replace(":", "").replace("-", "").strip()
        if len(mac_hex) != 12:
            raise ValueError(
                "La MAC debe tener 12 caracteres hexadecimales"
            )

        try:
            mac_bytes = bytes.fromhex(mac_hex)
        except ValueError as exc:
            raise ValueError(f"MAC inválida: '{data2}'") from exc

        data_bytes = broadcast_address.packed + mac_bytes
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
            args.hex,
            args.data2
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    message = build_message(command)

    # print("Mensaje hex:")
    # print(message.hex().upper())

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


if __name__ == "__main__":
    main()