# philiprehberger-mqtt-client

Simplified MQTT pub/sub wrapper with auto-reconnect.

## Install

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

## Features

- Decorator-based subscriptions
- MQTT wildcard support (`+` and `#`)
- Auto-reconnect with exponential backoff
- JSON publish/subscribe helpers
- TLS support (`mqtts://`)
- Last will and testament
- Authentication

## License

MIT
