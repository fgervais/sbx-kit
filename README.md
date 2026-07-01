# sbx-kit

A collection of [Docker Sandboxes] mixin kits for embedded development
workflows. Each kit is a `spec.yaml` that can be applied to a sandbox to
install tools, expose host peripherals, and deliver agent skills.

## Usage

Reference a kit in your sandbox configuration using its path in this
repository. Kits follow the [sbx mixin spec].

[Docker Sandboxes]: https://docs.docker.com/ai/sandboxes/
[sbx mixin spec]: https://github.com/docker/sbx-kits-contrib/tree/main/spec

## Kits

### [agentsmd](agentsmd/)

Delivers a shared [AGENTS.md] with baseline agent instructions and symlinks
Copilot's `copilot-instructions.md` to it, so both read the same source —
no tools installed.

[AGENTS.md]: https://agents.md/

### [fgervais-skills](fgervais-skills/)

Delivers additional agent skills into the sandbox — no tools installed.
Currently includes a [Bubbletea] skill for building Go TUI applications.

[Bubbletea]: https://github.com/charmbracelet/bubbletea

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

### [mcp-ampy](mcp-ampy/)

Connects the [Crush] agent to a [mcp-ampy] MCP server running on the host.
Registers the `ampy` HTTP MCP in Crush, giving the agent direct access to
a MicroPython board over serial — no serial passthrough into the sandbox
required.

[Crush]: https://github.com/charmbracelet/crush
[mcp-ampy]: https://github.com/fgervais/mcp-ampy
