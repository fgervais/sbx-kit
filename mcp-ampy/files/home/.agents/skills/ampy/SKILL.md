---
name: ampy
description: >-
  Interact with a MicroPython board over serial via the ampy MCP server
  running on the host. Use when reading, writing, or executing code on
  a connected MicroPython device (ESP32, RP2040, STM32, etc.).
---

# MicroPython Board (ampy)

A `mcp-ampy` MCP server running on the host exposes the connected
MicroPython board. It is registered in Crush as the `ampy` MCP.

## Available tools

| Tool         | Description                                          |
|--------------|------------------------------------------------------|
| `ls`         | List files/directories on the board                  |
| `mkdir`      | Create a directory on the board                      |
| `rm`         | Remove a file or directory from the board            |
| `put`        | Write a file to the board                            |
| `get`        | Read a file from the board                           |
| `exec`       | Execute MicroPython code (non-blocking)              |
| `read`       | Read buffered output from the last `exec` call       |
| `exec_stop`  | Interrupt a running `exec` and collect remaining output |

## Usage patterns

### List files

```
ls(directory="/", recursive=False)
```

### Upload a file

```
put(filename="/main.py", content="print('hello')\n")
```

### Execute code and read output

```
exec(code="import sys; print(sys.version)")
read(timeout=2)
```

For long-running code, call `read()` repeatedly until `done` is `true`,
then optionally call `exec_stop()` to interrupt.

## Troubleshooting

- **Connection refused**: `mcp-ampy` is not running on the host, or is
  bound to a different port than `$AMPY_PORT` (default `8000`).
- **Serial port error**: the board is disconnected or another process
  holds the serial port on the host.
