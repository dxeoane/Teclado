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
