# philiprehberger-mqtt-client

[![Tests](https://github.com/philiprehberger/py-mqtt-client/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-mqtt-client/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-mqtt-client.svg)](https://pypi.org/project/philiprehberger-mqtt-client/)
[![License](https://img.shields.io/github/license/philiprehberger/py-mqtt-client)](LICENSE)

Simplified MQTT pub/sub wrapper with auto-reconnect.

## Installation

```bash
pip install philiprehberger-mqtt-client
```

## Usage

```python
from philiprehberger_mqtt_client import MQTTClient

client = MQTTClient("mqtt://localhost:1883", client_id="my-app")

@client.on("home/temperature")
def on_temperature(topic, payload):
    print(f"Temperature: {float(payload)}°C")

@client.on("home/+/status")  # wildcard
def on_device_status(topic, payload):
    device = topic.split("/")[1]
    print(f"{device}: {payload}")

# Publish
client.publish("home/lights/living", "on")
client.publish_json("home/sensors/data", {"temp": 22.5, "humidity": 45})

# Connect (blocks with auto-reconnect)
client.connect()

# Or background mode
client.connect(background=True)
```

## API

| Function / Class | Description |
|------------------|-------------|
| `MQTTClient(broker_url, client_id, username, password, ...)` | Simplified MQTT client with decorator-based subscriptions and auto-reconnect |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## License

MIT
