# Rkbd

Permite enviar comandos a un teclado remoto

## Librerias necesarias

### Librerias externas (instalar con pip)

- `python-dotenv`
- `cryptography`
- `paho-mqtt`

Instalacion:

```bash
pip install python-dotenv cryptography paho-mqtt
```

## Version recomendada de Python

- Python 3.9 o superior.

## Variables de entorno esperadas

Para que el script funcione correctamente, define estas variables (por ejemplo, en un archivo `.env`):

- `MQTT_HOST`
- `MQTT_PORT`
- `MQTT_TOPIC`
- `MQTT_USER`
- `MQTT_PASSWORD`
- `AES_KEY` (hex)
- `HMAC_KEY` (hex)

## Uso de wake_on_lan

`wake_on_lan` ahora recibe la IP de broadcast y la MAC por separado:

```bash
python rkbd_send.py wake_on_lan 192.168.10.255 001122334455
```

## Uso de ping

```bash
python rkbd_send.py ping
```

También acepta `10` o `0x0A`. La orden se cifra y autentica como las demás.
Tras validarla, el dispositivo publica `PONG AA:BB:CC:DD:EE:FF` con su MAC WiFi
en el mismo `MQTT_TOPIC`, como texto plano y sin retención. El cliente solo
envía la orden; para ver la respuesta hay que estar suscrito al topic.
