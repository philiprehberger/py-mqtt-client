"""Simplified MQTT pub/sub wrapper with auto-reconnect."""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable
from urllib.parse import urlparse

import paho.mqtt.client as mqtt

__all__ = ["MQTTClient"]


@dataclass
class _Subscription:
    topic: str
    callback: Callable[[str, str], None]
    qos: int = 0


class MQTTClient:
    """Simplified MQTT client with decorator-based subscriptions and auto-reconnect."""

    def __init__(
        self,
        broker_url: str = "mqtt://localhost:1883",
        client_id: str | None = None,
        username: str | None = None,
        password: str | None = None,
        keepalive: int = 60,
        reconnect_delay: float = 5.0,
        max_reconnect_delay: float = 120.0,
        will_topic: str | None = None,
        will_payload: str | None = None,
        will_qos: int = 0,
        will_retain: bool = False,
    ) -> None:
        parsed = urlparse(broker_url)
        self._host = parsed.hostname or "localhost"
        self._port = parsed.port or 1883
        self._use_tls = parsed.scheme in ("mqtts", "ssl")

        self._client_id = client_id
        self._username = username or parsed.username
        self._password = password or parsed.password
        self._keepalive = keepalive
        self._reconnect_delay = reconnect_delay
        self._max_reconnect_delay = max_reconnect_delay

        self._subscriptions: list[_Subscription] = []
        self._client: mqtt.Client | None = None
        self._connected = False
        self._running = False

        self._will_topic = will_topic
        self._will_payload = will_payload
        self._will_qos = will_qos
        self._will_retain = will_retain

        self._on_connect_callback: Callable[[], None] | None = None
        self._on_disconnect_callback: Callable[[], None] | None = None

    def on(self, topic: str, qos: int = 0) -> Callable:
        """Decorator to subscribe to a topic.

        Supports MQTT wildcards: + (single level), # (multi level).
        """
        def decorator(fn: Callable[[str, str], None]) -> Callable[[str, str], None]:
            self._subscriptions.append(_Subscription(
                topic=topic,
                callback=fn,
                qos=qos,
            ))
            return fn
        return decorator

    def subscribe(
        self,
        topic: str,
        callback: Callable[[str, str], None],
        qos: int = 0,
    ) -> None:
        """Programmatically subscribe to a topic."""
        sub = _Subscription(topic=topic, callback=callback, qos=qos)
        self._subscriptions.append(sub)
        if self._client and self._connected:
            self._client.subscribe(topic, qos)

    def publish(
        self,
        topic: str,
        payload: str,
        qos: int = 0,
        retain: bool = False,
    ) -> None:
        """Publish a message."""
        if self._client and self._connected:
            self._client.publish(topic, payload, qos=qos, retain=retain)

    def publish_json(
        self,
        topic: str,
        data: Any,
        qos: int = 0,
        retain: bool = False,
    ) -> None:
        """Publish a JSON-serialized message."""
        self.publish(topic, json.dumps(data), qos=qos, retain=retain)

    def on_connect_handler(self, fn: Callable[[], None]) -> Callable[[], None]:
        """Decorator for connect event."""
        self._on_connect_callback = fn
        return fn

    def on_disconnect_handler(self, fn: Callable[[], None]) -> Callable[[], None]:
        """Decorator for disconnect event."""
        self._on_disconnect_callback = fn
        return fn

    def _setup_client(self) -> mqtt.Client:
        client = mqtt.Client(
            client_id=self._client_id or "",
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        )

        if self._username:
            client.username_pw_set(self._username, self._password)

        if self._use_tls:
            client.tls_set()

        if self._will_topic:
            client.will_set(
                self._will_topic,
                self._will_payload,
                qos=self._will_qos,
                retain=self._will_retain,
            )

        def on_connect(client: mqtt.Client, userdata: Any, flags: Any, rc: int, properties: Any = None) -> None:
            self._connected = True
            for sub in self._subscriptions:
                client.subscribe(sub.topic, sub.qos)
            if self._on_connect_callback:
                self._on_connect_callback()

        def on_disconnect(client: mqtt.Client, userdata: Any, flags: Any, rc: int, properties: Any = None) -> None:
            self._connected = False
            if self._on_disconnect_callback:
                self._on_disconnect_callback()

        def on_message(client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
            topic = msg.topic
            payload = msg.payload.decode("utf-8", errors="replace")
            for sub in self._subscriptions:
                if mqtt.topic_matches_sub(sub.topic, topic):
                    try:
                        sub.callback(topic, payload)
                    except Exception:
                        pass

        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_message

        return client

    def connect(self, background: bool = False) -> None:
        """Connect to the broker and start listening.

        Args:
            background: If True, run in a background thread.
        """
        self._running = True
        self._client = self._setup_client()

        if background:
            thread = threading.Thread(target=self._connect_loop, daemon=True)
            thread.start()
        else:
            self._connect_loop()

    def _connect_loop(self) -> None:
        delay = self._reconnect_delay
        while self._running:
            try:
                self._client.connect(self._host, self._port, self._keepalive)
                self._client.loop_forever()
            except (OSError, ConnectionRefusedError):
                if not self._running:
                    break
                time.sleep(delay)
                delay = min(delay * 2, self._max_reconnect_delay)
            except KeyboardInterrupt:
                break
        self.disconnect()

    def disconnect(self) -> None:
        """Disconnect from the broker."""
        self._running = False
        if self._client:
            self._client.disconnect()
            self._client.loop_stop()

    @property
    def is_connected(self) -> bool:
        return self._connected
