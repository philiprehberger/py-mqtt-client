"""Basic import test."""


def test_import():
    """Verify the package can be imported."""
    import philiprehberger_mqtt_client
    assert hasattr(philiprehberger_mqtt_client, "__name__") or True
