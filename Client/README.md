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

## Wake-on-LAN

Los datos del comando contienen primero los 4 bytes de la dirección IPv4 de
broadcast y después los 6 bytes de la MAC del equipo que se quiere despertar.
Por ejemplo, para broadcast `192.168.1.255` y MAC `00:11:22:33:44:55`:

```bash
python rkbd_send.py --hex wake_on_lan c0a801ff001122334455
```
