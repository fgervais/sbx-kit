# sbx-kit

A collection of [Docker Sandboxes] mixin kits for embedded development
workflows. Each kit is a `spec.yaml` that can be applied to a sandbox to
install tools, expose host peripherals, and deliver agent skills.

## Usage

Reference a kit in your sandbox configuration using its path in this
repository. Kits follow the [sbx mixin spec].

[Docker Sandboxes]: https://docs.github.com/en/copilot/using-github-copilot/using-claude-sonnet-in-github-copilot
[sbx mixin spec]: https://github.com/github/docker-sandboxes

## Kits

### [pyocd](pyocd/)

Installs [pyOCD] and connects to a host debug probe served over TCP via
`pyocd server --allow-remote`. Enables flashing firmware, running a GDB
server, resetting, and erasing flash on an embedded target — no probe
passthrough required inside the sandbox.

[pyOCD]: https://pyocd.io

### [serial-console](serial-console/)

Installs [pyserial] and connects to a host serial port proxied over TCP via
`socat`. Enables reading and writing to an embedded board's UART console
directly from Python — no virtual device or special drivers needed inside
the sandbox.

[pyserial]: https://pyserial.readthedocs.io
