---
name: serial-console
description: >-
  Access the host serial console proxied over TCP via socat. Covers
  connecting with pyserial, reading output, and sending commands.
globs:
  - "**/*.py"
---

# Serial Console Access

The host's serial port is bridged into the sandbox over TCP via socat. The user
has set this up on the host before starting the sandbox. Connect to it directly
from Python — no virtual device, no special drivers needed.

## Connection

The endpoint is configured via two environment variables:

- `SERIAL_HOST` — host running the socat TCP bridge
- `SERIAL_PORT` — TCP port socat is listening on

```python
import os
import serial

ser = serial.serial_for_url(
    f'socket://{os.environ["SERIAL_HOST"]}:{os.environ["SERIAL_PORT"]}',
    timeout=1,
)
```

## Reading output

```python
# Read one line (waits up to `timeout` seconds)
line = ser.readline()
print(line.decode("utf-8", errors="replace").strip())

# Read all available output (non-blocking)
import time
time.sleep(0.5)
data = ser.read(ser.in_waiting or 1)
print(data.decode("utf-8", errors="replace"))
```

## Sending commands

```python
ser.write(b"kernel reboot\n")
```

## Full read/write example

```python
import os, time, serial

ser = serial.serial_for_url(
    f'socket://{os.environ["SERIAL_HOST"]}:{os.environ["SERIAL_PORT"]}',
    timeout=2,
)

# Send a command and collect the response
ser.write(b"shell\n")
time.sleep(0.1)
response = ser.read(ser.in_waiting or 1)
print(response.decode("utf-8", errors="replace"))

ser.close()
```

## Raw socket alternative

If pyserial is not available, use the standard `socket` module:

```python
import os, socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((os.environ["SERIAL_HOST"], int(os.environ["SERIAL_PORT"])))
s.sendall(b"shell\n")
print(s.recv(4096).decode("utf-8", errors="replace"))
s.close()
```

## Troubleshooting

**Connection refused** — the host-side socat bridge is not running. Ask the user
to start it on the host before retrying.

**No output / timeout** — the board may not be sending data. Try nudging it:
```python
ser.write(b"\n")
time.sleep(0.2)
print(ser.read(ser.in_waiting or 1))
```

**Garbled output** — baud rate mismatch between the host socat configuration and
the board firmware. Ask the user to verify the baud rate on the host side.

**Test connectivity** (without pyserial):
```bash
nc -zv "$SERIAL_HOST" "$SERIAL_PORT"
```