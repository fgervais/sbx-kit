---
name: ampy
description: >-
  Interact with a MicroPython board via the ampy MCP server running on
  the host. The MCP is registered in Crush as `ampy`.
---

# MicroPython Board (ampy)

## Prerequisites

The `mcp-ampy` server must be running on the host before using the MCP.
If it is not running, ask the user to start it. Example using Docker:

```sh
docker run --rm -p 8000:8000 \
  --device /dev/ttyACM0 \
  ghcr.io/fgervais/mcp-ampy \
  --port /dev/ttyACM0
```

The serial device (`/dev/ttyACM0`) and image tag may vary.

## Troubleshooting

- **Connection refused**: `mcp-ampy` is not running on the host, or is
  bound to a different port than `$AMPY_PORT` (default `8000`).
- **Serial port error**: the board is disconnected or another process
  holds the serial port on the host.
