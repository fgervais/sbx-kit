# `zephyr-mymodule-base` module

Source: https://github.com/fgervais/zephyr-mymodule-base

Shared west module used by every `project-nrf-*` app. It provides
cross-project infrastructure so apps don't reimplement it: reset-cause
inspection, a stable per-device unique ID, watchdog setup, OpenThread
network management, and an MQTT-based Home Assistant integration.

One of the two shared modules under our control (see
[Module ownership](../SKILL.md#module-ownership)) — don't modify it
unilaterally.

## API stability — read the pinned revision, not this file

Each project pins its own `zephyr-mymodule-base` revision in `west.yml`,
and the module's public API changes over time. **Function signatures,
include paths, Kconfig names, and defaults do drift between revisions**,
and different projects legitimately differ — e.g. `ha_start()` and the
`*_retry()` helpers have changed argument lists, and headers moved under
`mymodule/base/`.

So this file describes *concepts, patterns, and rationale*, not exact
signatures or values. For the real API a project builds against, always
read both:

- the module headers under `include/mymodule/base/` at that project's
  pinned revision, and
- that project's own `app/src/main.c`, which matches its pinned revision.

Treat any signature or number shown here as illustrative — verify against
those two sources before writing code.

## Structure

```
Kconfig, Kconfig.<feature>   # per-feature Kconfig, rsourced from the root Kconfig
CMakeLists.txt               # conditionally compiles each src/<feature>.c
zephyr/module.yml            # west module manifest
include/mymodule/base/*.h    # public headers, included as <mymodule/base/xxx.h>
src/*.c                      # one .c per feature, gated by its Kconfig option
```

Features are gated independently, so an app only compiles what it enables.
Current set (verify against the pinned revision's `Kconfig.*`):

| Feature (`MY_MODULE_BASE_*`) | Header             | Provides |
|------------------------------|--------------------|----------|
| `RESET`                      | `reset.h`          | reset-cause read/clear + `is_reset_cause_*()` classifiers |
| `UID`                        | `uid.h`            | stable per-device unique ID from the SoC hardware ID |
| `WATCHDOG`                   | `watchdog.h`       | install/feed watchdog channels (one shared timeout) |
| `OPENTHREAD`                 | `openthread.h`     | OpenThread start + SED latency management |
| `HOME_ASSISTANT`             | `ha.h`, `mqtt.h`   | HA sensors/triggers over MQTT (selects `UID`) |

`HOME_ASSISTANT` builds on `UID` (for stable entity IDs) and adds
sub-options for device name, device type, and MQTT server.

## Enabling it

1. Add it to `west.yml` as a project pinned to a specific revision:

   ```yaml
   - name: zephyr-mymodule-base
     url: https://github.com/fgervais/zephyr-mymodule-base.git
     revision: <pinned-sha>
     path: mymodules/base
   ```

2. Enable the features you need in `app/prj.conf`, e.g.:

   ```conf
   CONFIG_MY_MODULE_BASE_RESET=y
   CONFIG_MY_MODULE_BASE_UID=y
   CONFIG_MY_MODULE_BASE_HOME_ASSISTANT=y
   CONFIG_MY_MODULE_BASE_HA_MQTT_SERVER_HOSTNAME="home.home.arpa"
   ```

   The MQTT server is a **hostname resolved via DNS** at startup (the HA
   feature pulls in the DNS resolver), not an IP. `home.arpa` is the
   reserved home-network domain (RFC 8375) — network-specific, not
   portable; set it to whatever resolves to the broker on the target
   network.

3. Include headers as `<mymodule/base/xxx.h>` and initialize each enabled
   feature early in `main()`, respecting dependencies (init UID and bring
   the network up before starting the HA/MQTT integration).

## Patterns

The value of these projects is a handful of recurring patterns. Each is
described as: what it's for, why, and the project to copy it from. Read
that project's current `app/src/main.c` for the exact API.

### main() bring-up order

Rough order the apps follow: start + feed watchdog → read/clear reset
cause → init UID → start OpenThread and wait for the network → start
HA/MQTT → register sensors/triggers → set device online → suspend console
→ enter main loop. Ordering matters: later steps depend on earlier ones
(HA needs a unique ID and a reachable network).

> After OpenThread reports ready, the apps add a short fixed `k_sleep`
> before starting MQTT, with a "something else isn't ready yet" comment.
> The root cause is unidentified; keep the delay when copying the
> pattern. Worth replacing with a wait on the real condition if anyone
> root-causes it.

### Exposing a Home Assistant sensor

Examples: `manhole-water-level` (analog), `leak-detector` (binary).

- Declare a `struct ha_sensor` with its static fields (`type`, `name`,
  `device_class`, units, `retain`, ...); leave `unique_id` to be filled
  in at runtime.
- Build `unique_id` from the `uid_*` API (see source choice below). The
  buffer is small and fixed-size (`UID_UNIQUE_ID_STRING_SIZE` in
  `uid.h`) and the SoC ID already consumes much of it, so keep the
  part/sensor name components short — the generator truncates silently.
- Register the sensor and set the device online once MQTT is up; both
  depend on the broker being reachable, so use the retry helpers.
- For analog values the API separates accumulate from publish: add each
  sample cheaply (no MQTT, call it often) and publish periodically
  (averages the accumulated samples, publishes once, resets). This
  decouples sample rate from publish rate.
- `retain` sets the MQTT retain flag so the broker replays the last state
  to Home Assistant on reconnect. **Leave it off by default** — only
  retain values that represent *persistent state* which must survive
  until it next changes. Retain a latching condition that would otherwise
  be lost, e.g. `leak-detector`'s leak state (the device powers off right
  after publishing, so without retain HA shows nothing until a next
  publish that may never come). Do *not* retain momentary or
  continuously-refreshed readings (e.g. a room temperature): a stale
  retained value would just be replayed as if current, and a fresh
  reading is coming soon anyway.

A common concrete instance: a `problem` binary sensor named "Watchdog",
ID'd from the SoC, set from `is_reset_cause_watchdog()` at boot and
auto-cleared once the device has run healthily for a bit — surfaces
device hangs in the HA UI. Example: `thread-switch`.

### Choosing the unique-ID source

`unique_id` must be stable and collision-free. Pick its source by *what
the entity reports on*:

- **The board/SoC itself** (e.g. `leak-detector`'s leak sensor from an
  on-board comparator, or a watchdog/reset sensor): use the SoC unique ID
  (`uid_get_device_id()`). This is the *correct* choice, not a fallback —
  identity should track the board.
- **An external part with its own hardware serial** (e.g. a TMP117 with
  an EEPROM serial): use that serial, so the entity tracks the physical
  part rather than the board it's wired to. May mean building the ID
  string directly (e.g. adding a bus/channel index for multiple identical
  parts).
- **An external part with no ID of its own** (e.g. a GPIO distance
  sensor): fall back to the SoC unique ID for lack of anything better.

### OpenThread Sleepy End Device (SED)

Battery nodes join as an SED (`CONFIG_OPENTHREAD_MTD_SED=y`) so the radio
mostly sleeps, polling for Rx on a slow period. The module applies
SED-appropriate defaults and runs a latency-management thread: the app
can request a temporary fast-poll window (`openthread_request_low_latency`
/ `_normal_latency`) around a time-sensitive exchange, then fall back to
the slow period.

SED-specific Kconfig (channel, network name, xpanid, `MTD_SED`) is kept in
a separate `thread-sed.conf` added via `OVERLAY_CONFIG` in
`app/CMakeLists.txt`, not in `prj.conf` — easy to spot and swap per board.
Example: `leak-detector`.

Two power strategies sit on top of SED:

- **System ON** (`thread-switch`): stays running on a normal `k_sleep`
  main loop. Can *transmit* the instant an event happens (e.g. a button
  press) but Rx/replies lag by up to a poll interval. Good for
  input-driven nodes that must send promptly yet needn't be promptly
  reachable.
- **System Off** (`leak-detector`): after a one-shot task it publishes,
  then fully powers down (`sys_poweroff()`; needs `CONFIG_POWEROFF` +
  `CONFIG_PM_DEVICE`), waking via an interrupt source (e.g. LPCOMP) into a
  full reset. Near-zero current between events. Because wake is a full
  reset, the boot path *must* branch on reset cause (below) to tell a
  wake-from-event apart from a cold boot.

### Watchdog channels and the shared timeout

`watchdog_new_channel()` can install several channels on the same device.
`thread-switch` uses two: one fed every main-loop iteration, and one fed
by the module's MQTT code only on ping-response from the broker
(`mqtt_watchdog_init()`). The second couples the watchdog to *real server
round-trips*, not just to the loop running — so a stuck network path still
forces a reset even while the loop spins.

Gotcha: **all channels share one timeout**
(`CONFIG_MY_MODULE_BASE_WATCHDOG_TIMEOUT_SEC` — one global value, no
per-channel timeout). Size it for the *slowest*-fed channel. A
network-coupled channel is fed only as often as the MQTT keepalive (plus
reconnect time), so the timeout must sit well above that keepalive
interval — `thread-switch` runs a much larger timeout than the module
default for exactly this. Re-check the value whenever you add a channel
tied to a slow/external event; it affects every channel.

### Reset-cause branching and self-triggered "fast boot"

Read and clear the reset cause first thing at boot, then branch (example:
`thread-switch`):

- **Watchdog or button reset** → erase OpenThread persistent info
  (`openthread_erase_persistent_info()`) and rejoin fresh: the prior run
  crashed, or the user forced a reset, so don't trust stored network
  state.
- **Self-triggered reboot ("fast boot")** → skip work already done. On an
  unrecoverable runtime error the app reboots itself via
  `sys_reboot(<token>)`, stashing a sentinel in a retained register (nRF
  GPREGRET — survives reset but not power-loss). The next boot detects
  "software reset + our token" and takes a cheaper path: skip HA discovery
  re-publish (the broker still retains it), skip forced network rejoin
  (reuse credentials), skip reporting a watchdog event that didn't happen.
  Result: fast recovery from a transient error instead of a full cold
  boot.

System Off wake (`leak-detector`) is the same idea from the other side:
the `is_reset_cause_*()` classifiers are what let the app take a minimal
alert-only path on a wake-from-event versus a full startup on a normal
boot.
