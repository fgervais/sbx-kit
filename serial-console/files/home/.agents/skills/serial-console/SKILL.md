---
name: serial-console
description: >-
  Access the host serial console proxied over TCP via socat. Covers the
  serialcon.py bridge daemon for reading output, sending commands, and
  waiting for expected output.
globs:
  - "**/*.py"
---

# Serial Console Access

The host's serial port is bridged into the sandbox over TCP via socat. The user
sets this up on the host before starting the sandbox. The endpoint is given by
two environment variables:

- `SERIAL_HOST` — host running the socat TCP bridge
- `SERIAL_PORT` — TCP port socat is listening on

Use `scripts/serialcon.py` (in this skill's directory) to talk to it. Do not
open the socket directly for normal work; see "Why a daemon" below.

## Start the bridge

```bash
scripts/serialcon.py start     # background daemon; prints its log path
scripts/serialcon.py status    # endpoint, daemon pid, log size
```

Everything the board prints from this moment on is appended to the log, whether
or not you are actively looking. Start the daemon once, then leave it running
for the rest of the session.

## Read output

```bash
scripts/serialcon.py tail -n 40
```

The log is a plain file, so any normal tool works on it — use the log path from
`status` to grep it, count occurrences, or read it with the `read` tool:

```bash
LOG=$(scripts/serialcon.py status | awk '/^log:/ {print $2}')
grep -c 'MPU FAULT' "$LOG"
```

## Send commands

```bash
scripts/serialcon.py send 'kernel reboot'   # newline appended
scripts/serialcon.py send --raw $'\x03'     # raw bytes, no newline (Ctrl-C)
```

## Wait for expected output

`wait` blocks until a string appears, and exits non-zero on timeout. Prefer it
over `sleep`: it turns "did the board come back?" into one deterministic step
with a real exit code, and returns as soon as the output appears.

```bash
scripts/serialcon.py wait 'Booting nRF Connect SDK' --timeout 20
```

By default `wait` only considers output that arrives after it starts, so it
cannot match a stale hit from an earlier run. Pass `--from-start` to search the
whole log instead.

A reset-and-confirm cycle, which is the common case:

```bash
scripts/serialcon.py clear                  # truncate log, so matches are fresh
scripts/serialcon.py send 'kernel reboot'
scripts/serialcon.py wait 'Booting nRF Connect SDK' --timeout 20
```

## Housekeeping

```bash
scripts/serialcon.py clear   # truncate the log (it grows unbounded)
scripts/serialcon.py stop    # stop the daemon
```

When shutting down, stop before clearing. The daemon writes a final line to the
log as it exits, so clearing first leaves that line behind in a log you meant to
empty:

```bash
scripts/serialcon.py stop
scripts/serialcon.py clear
```

Clearing while the daemon keeps running is fine — it appends, so it continues at
the start of the truncated log rather than leaving a gap.

Set `SERIALCON_DIR` to use a separate log and daemon, e.g. to talk to a second
endpoint; one daemon runs per directory.

## Why a daemon

Three properties of this setup make one-shot `nc`/`socat`/pyserial invocations
the wrong tool. Keep them in mind before "simplifying" this to a bare command:

- **Each shell command is a separate process.** A per-command client is
  connected only while it runs, so anything printed between commands is lost —
  typically the boot banner, a watchdog reset, or a fault dump.
- **The network proxy requires the client to send data first.** On a raw TCP
  connection the proxy does not complete the tunnel until the client writes, so
  a connection that only reads receives nothing and is dropped after a few
  seconds. The daemon sends one byte on every connect to handle this.
- **Only one reader may consume the stream.** The host socat bridge accepts
  multiple connections, and a second reader silently takes part of the output.
  The daemon keeps the single connection and accepts data to transmit over a
  FIFO, so `send` does not open a competing one.

The daemon also reconnects on its own, with exponential backoff, so a board
reset or a restarted host bridge does not need manual intervention.

## Troubleshooting

**`send` reports the daemon is not running** — run `start` first.

**Connection refused in the log** — the host-side socat bridge is not running.
Ask the user to start it on the host; the daemon keeps retrying, so it will pick
the bridge up once it appears.

**No new output** — confirm the daemon is connected with `status`, then nudge
the board and look again:

```bash
scripts/serialcon.py send ''      # sends a bare newline
scripts/serialcon.py tail -n 20
```

**Garbled output** — baud rate mismatch between the host socat configuration
and the board firmware. Ask the user to verify the baud rate on the host side.

**Checking the bridge without the daemon** — as a last resort, to test whether
the bridge itself is alive. Note the `sendall` before the read: it is required,
not optional, and omitting it makes a working bridge look dead.

```bash
python3 -c 'import os, socket
s = socket.create_connection((os.environ["SERIAL_HOST"],
                              int(os.environ["SERIAL_PORT"])), timeout=10)
s.sendall(b"\n")                 # REQUIRED before reading; see "Why a daemon"
print(s.recv(4096).decode("utf-8", "replace"))'
```

Stop the daemon before running this, so the two do not compete for the stream.
