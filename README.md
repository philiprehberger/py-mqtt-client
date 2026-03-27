# philiprehberger-mqtt-client

[![Tests](https://github.com/philiprehberger/py-mqtt-client/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-mqtt-client/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-mqtt-client.svg)](https://pypi.org/project/philiprehberger-mqtt-client/)
[![GitHub release](https://img.shields.io/github/v/release/philiprehberger/py-mqtt-client)](https://github.com/philiprehberger/py-mqtt-client/releases)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-mqtt-client)](https://github.com/philiprehberger/py-mqtt-client/commits/main)
[![License](https://img.shields.io/github/license/philiprehberger/py-mqtt-client)](LICENSE)
[![Bug Reports](https://img.shields.io/github/issues/philiprehberger/py-mqtt-client/bug)](https://github.com/philiprehberger/py-mqtt-client/issues?q=is%3Aissue+is%3Aopen+label%3Abug)
[![Feature Requests](https://img.shields.io/github/issues/philiprehberger/py-mqtt-client/enhancement)](https://github.com/philiprehberger/py-mqtt-client/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
[![Sponsor](https://img.shields.io/badge/sponsor-GitHub%20Sponsors-ec6cb9)](https://github.com/sponsors/philiprehberger)

Simplified MQTT pub/sub wrapper with auto-reconnect.

## Installation

```bash
pip install philiprehberger-mqtt-client
```

## Usage

### Basic Pub/Sub

```python
from philiprehberger_mqtt_client import MQTTClient

client = MQTTClient("mqtt://localhost:1883", client_id="my-app")

@client.on("home/temperature")
def on_temperature(topic, payload):
    print(f"Temperature: {float(payload)}C")

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

### Offline Message Queue

Messages published while disconnected are automatically queued and sent when the connection is re-established.

```python
client = MQTTClient("mqtt://localhost:1883", offline_queue_size=500)

# These are queued if not yet connected
client.publish("sensors/temp", "22.5")
client.publish_json("sensors/data", {"humidity": 45})

# Check queue status
print(f"Pending messages: {client.pending_count()}")

# Connect — queued messages are flushed automatically
client.connect(background=True)

# Discard queued messages if needed
client.clear_queue()
```

## API

| Function / Class | Description |
|------------------|-------------|
| `MQTTClient(broker_url, client_id, ...)` | Simplified MQTT client with auto-reconnect and offline queue |
| `.on(topic, qos)` | Decorator to subscribe to a topic (supports MQTT wildcards) |
| `.subscribe(topic, callback, qos)` | Programmatically subscribe to a topic |
| `.publish(topic, payload, qos, retain)` | Publish a message (queues if disconnected) |
| `.publish_json(topic, data, qos, retain)` | Publish a JSON-serialized message |
| `.connect(background)` | Connect to the broker and start listening |
| `.disconnect()` | Disconnect from the broker |
| `.pending_count()` | Return number of messages in the offline queue |
| `.clear_queue()` | Discard all queued messages |
| `.is_connected` | Whether the client is currently connected |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this package useful, consider giving it a star on GitHub — it helps motivate continued maintenance and development.

[![LinkedIn](https://img.shields.io/badge/Philip%20Rehberger-LinkedIn-0A66C2?logo=linkedin)](https://www.linkedin.com/in/philiprehberger)
[![More packages](https://img.shields.io/badge/more-open%20source%20packages-blue)](https://philiprehberger.com/open-source-packages)

## License

[MIT](LICENSE)
