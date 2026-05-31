"""Tests for MQTTClient.publish_many."""

from __future__ import annotations

from unittest.mock import MagicMock

from philiprehberger_mqtt_client import MQTTClient


def _make_connected_client() -> tuple[MQTTClient, MagicMock]:
    """Create an MQTTClient with a mocked, connected paho client."""
    client = MQTTClient("mqtt://localhost:1883")
    mock_paho = MagicMock()
    client._client = mock_paho
    client._connected = True
    return client, mock_paho


def test_publish_many_calls_underlying_publish_per_message() -> None:
    """Each tuple results in one publish call with the right topic and payload."""
    client, mock_paho = _make_connected_client()

    client.publish_many([("a", "1"), ("b", "2")])

    assert mock_paho.publish.call_count == 2
    mock_paho.publish.assert_any_call("a", "1", qos=0, retain=False)
    mock_paho.publish.assert_any_call("b", "2", qos=0, retain=False)


def test_publish_many_propagates_qos_and_retain() -> None:
    """qos and retain kwargs are passed through to every publish."""
    client, mock_paho = _make_connected_client()

    client.publish_many([("x", "1"), ("y", "2")], qos=2, retain=True)

    assert mock_paho.publish.call_count == 2
    mock_paho.publish.assert_any_call("x", "1", qos=2, retain=True)
    mock_paho.publish.assert_any_call("y", "2", qos=2, retain=True)


def test_publish_many_empty_list_is_noop() -> None:
    """An empty list results in no publish calls."""
    client, mock_paho = _make_connected_client()

    client.publish_many([])

    mock_paho.publish.assert_not_called()
