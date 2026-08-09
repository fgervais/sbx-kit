#!/usr/bin/env python3
"""Persistent serial-console bridge for the socat/TCP proxy.

Owns a single TCP connection to the host socat bridge, logs everything it
receives to a file, and accepts data to transmit via a FIFO.  A single reader
avoids output being split between competing connections, and the mandatory
first-byte "nudge" (required by the sandbox network proxy for raw TCP) is
handled once, on every (re)connect.

Usage:
    serialcon.py start            # start the background daemon
    serialcon.py send 'kernel reboot'
    serialcon.py send --raw $'\\x03'
    serialcon.py tail [-n 40]     # last N lines of the log
    serialcon.py wait 'MPU FAULT' [--timeout 30]
    serialcon.py status
    serialcon.py stop
    serialcon.py clear            # truncate the log
"""
import argparse
import os
import select
import signal
import socket
import sys
import time

RUN_DIR = os.environ.get("SERIALCON_DIR", "/tmp/serialcon")
LOG = os.path.join(RUN_DIR, "console.log")
FIFO = os.path.join(RUN_DIR, "tx.fifo")
PID = os.path.join(RUN_DIR, "daemon.pid")

HOST = os.environ.get("SERIAL_HOST", "host.docker.internal")
PORT = int(os.environ.get("SERIAL_PORT", "8000"))
NUDGE = b"\n"  # proxy requires the client to speak first

MIN_BACKOFF = 1.0    # seconds, first reconnect delay
MAX_BACKOFF = 30.0   # seconds, ceiling for repeated failures
HEALTHY_AFTER = 10.0  # a connection lasting this long resets the backoff


def _nap(seconds: float, cancelled) -> None:
    """Sleep in short slices so SIGTERM stays responsive during a backoff."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline and not cancelled():
        time.sleep(0.1)


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _daemon_pid():
    try:
        with open(PID) as fh:
            pid = int(fh.read().strip())
    except (OSError, ValueError):
        return None
    return pid if _alive(pid) else None


def _log(fh, text: str) -> None:
    fh.write(f"\n--- serialcon: {text} ---\n".encode())
    fh.flush()


def run_daemon() -> int:
    os.makedirs(RUN_DIR, exist_ok=True)
    if not os.path.exists(FIFO):
        os.mkfifo(FIFO, 0o600)
    with open(PID, "w") as fh:
        fh.write(str(os.getpid()))

    stop = False

    def _sigterm(*_):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGTERM, _sigterm)
    signal.signal(signal.SIGINT, _sigterm)

    # O_RDWR keeps the FIFO open even with no writer, so select() never
    # reports permanent EOF on it.
    fifo_fd = os.open(FIFO, os.O_RDWR | os.O_NONBLOCK)
    logfh = open(LOG, "ab", buffering=0)

    # Exponential backoff: a bridge that is down, or a peer that closes
    # immediately, must not be hammered with reconnect attempts.
    backoff = MIN_BACKOFF

    try:
        while not stop:
            try:
                sock = socket.create_connection((HOST, PORT), timeout=10)
            except OSError as exc:
                _log(logfh, f"connect failed: {exc}; retrying in {backoff:.1f}s")
                _nap(backoff, lambda: stop)
                backoff = min(backoff * 2, MAX_BACKOFF)
                continue

            sock.settimeout(None)
            sock.sendall(NUDGE)  # REQUIRED: initialise the tunnel
            _log(logfh, f"connected to {HOST}:{PORT} (nudged)")
            connected_at = time.monotonic()

            while not stop:
                try:
                    readable, _, _ = select.select([sock, fifo_fd], [], [], 1.0)
                except OSError:
                    break
                if fifo_fd in readable:
                    try:
                        tx = os.read(fifo_fd, 4096)
                    except BlockingIOError:
                        tx = b""
                    if tx:
                        try:
                            sock.sendall(tx)
                        except OSError as exc:
                            _log(logfh, f"write failed: {exc}")
                            break
                if sock in readable:
                    try:
                        data = sock.recv(8192)
                    except OSError as exc:
                        _log(logfh, f"read failed: {exc}")
                        break
                    if not data:
                        _log(logfh, "peer closed connection; reconnecting")
                        break
                    logfh.write(data)
            sock.close()
            # Only a connection that actually lasted is treated as healthy and
            # resets the backoff; instant drops keep escalating the delay.
            if time.monotonic() - connected_at >= HEALTHY_AFTER:
                backoff = MIN_BACKOFF
            else:
                backoff = min(backoff * 2, MAX_BACKOFF)
            if not stop:
                _log(logfh, f"reconnecting in {backoff:.1f}s")
                _nap(backoff, lambda: stop)
    finally:
        _log(logfh, "daemon exiting")
        logfh.close()
        os.close(fifo_fd)
        if os.path.exists(PID):
            os.unlink(PID)
    return 0


def cmd_start(args) -> int:
    pid = _daemon_pid()
    if pid:
        print(f"already running (pid {pid})")
        return 0
    os.makedirs(RUN_DIR, exist_ok=True)
    if os.fork() != 0:
        for _ in range(50):
            time.sleep(0.1)
            if _daemon_pid():
                break
        pid = _daemon_pid()
        print(f"started (pid {pid}), log: {LOG}" if pid else "failed to start")
        return 0 if pid else 1
    os.setsid()
    devnull = os.open(os.devnull, os.O_RDWR)
    for fd in (0, 1, 2):
        os.dup2(devnull, fd)
    sys.exit(run_daemon())


def cmd_send(args) -> int:
    if not _daemon_pid():
        print("daemon not running; run 'serialcon.py start' first", file=sys.stderr)
        return 1
    payload = args.data.encode() if args.raw else (args.data + "\n").encode()
    with open(FIFO, "wb", buffering=0) as fh:
        fh.write(payload)
    return 0


def cmd_tail(args) -> int:
    if not os.path.exists(LOG):
        print("no log yet", file=sys.stderr)
        return 1
    with open(LOG, "rb") as fh:
        lines = fh.read().splitlines()[-args.n:]
    sys.stdout.write("\n".join(l.decode("utf-8", "replace") for l in lines) + "\n")
    return 0


def cmd_wait(args) -> int:
    deadline = time.time() + args.timeout
    needle = args.pattern.encode()
    start = os.path.getsize(LOG) if os.path.exists(LOG) else 0
    if args.from_start:
        start = 0
    while time.time() < deadline:
        if os.path.exists(LOG):
            with open(LOG, "rb") as fh:
                fh.seek(start)
                if needle in fh.read():
                    print(f"found: {args.pattern}")
                    return 0
        time.sleep(0.2)
    print(f"timeout after {args.timeout}s waiting for: {args.pattern}", file=sys.stderr)
    return 1


def cmd_status(args) -> int:
    pid = _daemon_pid()
    size = os.path.getsize(LOG) if os.path.exists(LOG) else 0
    print(f"daemon:   {'running (pid %d)' % pid if pid else 'stopped'}")
    print(f"endpoint: {HOST}:{PORT}")
    print(f"log:      {LOG} ({size} bytes)")
    return 0 if pid else 1


def cmd_stop(args) -> int:
    pid = _daemon_pid()
    if not pid:
        print("not running")
        return 0
    os.kill(pid, signal.SIGTERM)
    for _ in range(30):
        time.sleep(0.1)
        if not _daemon_pid():
            break
    print("stopped")
    return 0


def cmd_clear(args) -> int:
    open(LOG, "wb").close()
    print("log cleared")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("start").set_defaults(fn=cmd_start)
    sub.add_parser("stop").set_defaults(fn=cmd_stop)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    sub.add_parser("clear").set_defaults(fn=cmd_clear)
    sub.add_parser("_daemon").set_defaults(fn=lambda a: run_daemon())

    s = sub.add_parser("send")
    s.add_argument("data")
    s.add_argument("--raw", action="store_true", help="do not append a newline")
    s.set_defaults(fn=cmd_send)

    t = sub.add_parser("tail")
    t.add_argument("-n", type=int, default=20)
    t.set_defaults(fn=cmd_tail)

    w = sub.add_parser("wait")
    w.add_argument("pattern")
    w.add_argument("--timeout", type=float, default=30.0)
    w.add_argument("--from-start", action="store_true")
    w.set_defaults(fn=cmd_wait)

    args = p.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
