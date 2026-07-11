# `project-nrf-template`

Source: https://github.com/fgervais/project-nrf-template

## Purpose

`project-nrf-template` is the starting point for every new
`project-nrf-*` application. A new project is created by copying this
repo, pointing its `origin` remote at the new project's own GitHub repo,
and building from there. It intentionally stays small and is kept up to
date so that starting a new board/product only means adding what's
different, not stripping out what isn't needed.

It wires together the two shared modules described elsewhere in this
skill — [`zephyr-my-boards`](../SKILL.md#module-ownership) for board
definitions and [`zephyr-mymodule-base`](mymodule-base.md) for shared
application infrastructure — plus a minimal, event-driven application
skeleton built on Zephyr's CAF (Common Application Framework).

## Structure

```
west.yml                    # west manifest: pulls in the nrf SDK, zephyr-my-boards,
                             # and zephyr-mymodule-base as projects
compose.yaml                # docker compose service used to build (ZEPHYR_BASE, working dir)
compose.device.yaml         # compose override that exposes /dev/bus/usb for flashing
pyocd.yaml                  # pyocd target config, used as an alternative to nrfjprog flashing
README.md                   # init/build/menuconfig/flash instructions for the template
app/                        # the actual Zephyr application ("self" project in west.yml)
  CMakeLists.txt            # sets BOARD_ROOT to the app itself, derives app version from
                             # `git describe`, adds configuration/<board> as an include dir
  Kconfig                   # app-level Kconfig options, sources Kconfig.zephyr
  app_version.h.in          # template for the generated app_version.h
  prj.conf                  # base project config: CAF, buttons, mymodule-base reset/watchdog
  src/main.c                # minimal main(): starts the watchdog, reports reset cause,
                             # initializes the CAF event manager, and runs an event loop
  boards/<board>.overlay    # per-board devicetree overlay (board-specific hardware)
  configuration/<board>/    # per-board headers included via zephyr_include_directories,
                             # e.g. button definitions consumed by CAF
```

The app layout follows Zephyr's "board root" + "board overlay/config
per board" convention so that adding support for a new board is mostly
additive: a new `boards/<board>.overlay` and `configuration/<board>/`
directory, without touching the shared `src/main.c` skeleton.

## What the skeleton already gives you

Out of the box (before any product-specific code is added), the template
provides basic, broadly useful functionality so most new projects don't
have to wire it up again:

- A CAF-based event manager and module-state tracking, with a button
  press wired to a `button_event`.
- Watchdog setup and feeding via `zephyr-mymodule-base`'s watchdog
  feature (`CONFIG_MY_MODULE_BASE_WATCHDOG`).
- Reset-cause reporting on boot via `zephyr-mymodule-base`'s reset
  feature (`CONFIG_MY_MODULE_BASE_RESET`).
- Thread analyzer output on boot and periodically in the main loop, for
  stack-usage visibility.
- An optional console-suspend path (`CONFIG_APP_SUSPEND_CONSOLE`) for
  power-sensitive designs.

Products that need OpenThread, MQTT, Home Assistant integration, or a
unique device ID pull those in by enabling the corresponding
`zephyr-mymodule-base` Kconfig options (see
[`mymodule-base.md`](mymodule-base.md)) — the template itself does not
enable them, keeping the base skeleton minimal.

## Starting a new project from it

1. Copy/clone `project-nrf-template`, then repoint `origin` at the new
   project's own repository (per the template's own README `west init`
   instructions).
2. Update `west.yml` if the new project needs a different `nrf` SDK
   revision, or additional west modules/projects.
3. Add board support: a devicetree overlay under `app/boards/` and, if
   needed, a `app/configuration/<board>/` directory for board-specific
   headers.
4. Enable the `zephyr-mymodule-base` features the product needs in
   `app/prj.conf`, and extend `app/src/main.c` with product logic on top
   of the existing event loop.
5. Build/flash using the docker compose + pyocd workflow documented in
   the template's own `README.md` (kept there rather than duplicated
   here, since it's the authoritative, up-to-date source).
