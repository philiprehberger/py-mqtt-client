# Changelog

## 0.2.1 (2026-03-31)

- Standardize README to 3-badge format with emoji Support section
- Update CI checkout action to v5 for Node.js 24 compatibility

## 0.2.0 (2026-03-27)

- Add offline message queue with auto-flush on reconnect
- Messages published while disconnected are queued and sent automatically on reconnect
- Add `MQTTClient.pending_count()` to check queued message count
- Add `MQTTClient.clear_queue()` to discard queued messages

## 0.1.8 (2026-03-22)

- Add pytest and mypy configuration to pyproject.toml

## 0.1.5

- Add basic import test

## 0.1.4

- Add Development section to README

## 0.1.1

- Add project URLs to pyproject.toml

## 0.1.0 (2026-03-10)

- Initial release
