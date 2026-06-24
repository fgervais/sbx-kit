---
name: pyocd
description: >-
  Guide for using pyOCD with a remote debug probe over TCP.
  Use this when flashing firmware, running a GDB server, resetting, or erasing
  flash on an embedded target via a remotely connected debug probe.
---

# pyOCD Remote Probe

A host debug probe (J-Link, CMSIS-DAP, ST-Link, etc.) is accessible over TCP
via pyOCD's remote probe server running on the host.

## Connecting

The probe is accessed via `--uid=remote:$PYOCD_HOST:$PYOCD_PORT`.

**Important:** You must always specify `--target` when using a remote probe.
Auto-detection does not work over the network.

### Flash firmware

```sh
pyocd flash \
  --uid=remote:${PYOCD_HOST}:${PYOCD_PORT} \
  --target <target> \
  firmware.bin
```

### Run GDB server

```sh
pyocd gdbserver \
  --uid=remote:${PYOCD_HOST}:${PYOCD_PORT} \
  --target <target>
```

Then connect with GDB:

```sh
arm-none-eabi-gdb firmware.elf
(gdb) target remote localhost:3333
```

### Reset target

```sh
pyocd reset \
  --uid=remote:${PYOCD_HOST}:${PYOCD_PORT} \
  --target <target>
```

### Erase flash

```sh
pyocd erase \
  --uid=remote:${PYOCD_HOST}:${PYOCD_PORT} \
  --target <target> \
  --chip
```

### Commander (interactive)

```sh
pyocd commander \
  --uid=remote:${PYOCD_HOST}:${PYOCD_PORT} \
  --target <target>
```

## Common targets

| Board / MCU | `--target` value |
|---|---|
| nRF52840 | `nrf52840` |
| nRF5340 | `nrf5340` |
| STM32F4xx | `stm32f401xc` (or specific variant) |
| RP2040 | `rp2040` |

Run `pyocd list --targets` for the full list.

## Troubleshooting

- **Connection refused**: the pyOCD server is not running on the host or is
  using a different port than `PYOCD_PORT`.
- **Target detection fails**: always pass `--target` explicitly — auto-detection
  is not supported for remote probes.
- **Missing target support**: install the pack with
  `pyocd pack install <target>` inside the sandbox, then retry.
