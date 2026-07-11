---
name: zephyr
description: >-
  Research and implementation guidance for Zephyr RTOS projects. Use when
  implementing a Zephyr feature, driver, subsystem, or board support to ensure
  you follow current upstream conventions and avoid deprecated patterns.
globs:
  - "**/*.c"
  - "**/*.h"
  - "**/*.yaml"
  - "**/*.yml"
  - "**/*Kconfig*"
  - "**/*.conf"
  - "**/*.overlay"
---

# Zephyr Implementation Guidance

Zephyr is a fast-moving project. Before implementing anything, research how it
is done in the upstream tree to avoid deprecated patterns.

## Research order

1. **Local `zephyr/` tree** — look at the root of the project in the `zephyr/`
   folder first. This is the version the project actually builds against.
2. **Samples and tests** — search `zephyr/samples/` and `zephyr/tests/` for
   working examples of the feature or subsystem you need.
3. **GitHub main branch** — the local tree may be behind. Cross-reference with
   https://github.com/zephyrproject-rtos/zephyr to see the current upstream
   state.
4. **`git blame`** — if you find a relevant implementation on GitHub, run
   `git blame` on it to check how recent it is. A very recent change may not
   be in the version the project uses yet.
5. **Pull requests** — search open and recently merged PRs on
   https://github.com/zephyrproject-rtos/zephyr/pulls for the feature or
   subsystem. The latest PRs show the direction maintainers are heading and
   their comments reveal expectations around API design and code style.

## Project base

Projects are normally based on `sdk-nrf`, which is itself based on Zephyr.
Check `sdk-nrf` samples and drivers as well:
https://github.com/nrfconnect/sdk-nrf

For additional project examples based on Zephyr (same author, same patterns),
see: https://github.com/fgervais/project-nrf-*

New projects normally start from a copy of **`project-nrf-template`**
(`origin` is repointed at the new project's own repo). For its structure,
purpose, and what it already provides, see
[`references/project-template.md`](references/project-template.md).

## Module ownership

Board definitions may come from the west module **`zephyr-my-boards`** and
shared code from **`zephyr-mymodule-base`**. Both modules are under our
control but changes to them require a discussion and agreement before
proceeding — do not modify them unilaterally. Raise the need and design the
change collaboratively first.

For `zephyr-mymodule-base`'s structure, purpose, and how a project consumes
it, see [`references/mymodule-base.md`](references/mymodule-base.md).

These modules' APIs change between revisions and each project pins its own,
so treat the headers at a project's pinned revision (and its own `main.c`)
as the source of truth — not older projects or docs.

## Networking

Projects stay **IPv6-only** — `CONFIG_NET_IPV6=y` with `CONFIG_NET_IPV4`
left disabled, whether the transport is Thread (IPv6-only by design) or
Wi-Fi (where IPv4/DHCPv4 is explicitly commented out rather than left
enabled by default). Do not enable IPv4 or add IPv4-specific networking
code unless there is a concrete new requirement — keep new projects
consistent with this convention.

## Power consumption

Always target the lowest power profile. Do not enable peripherals, clocks, or
subsystems that are not required by the application. Prefer device tree
`status = "disabled"` for unused nodes and avoid Kconfig options that pull in
unnecessary drivers or subsystems.

**Always suspend the console before entering the main sleep loop** on
battery-powered nodes. A UART console left active keeps its clock/peripheral
running and, on its own, accounts for a "huge" share of otherwise-idle power
draw compared to the rest of the system in normal System ON sleep — enough
to dominate battery life if left enabled. Every `project-nrf-*` app suspends
it once init is done, right before entering the main loop:

```c
pm_device_action_run(cons, PM_DEVICE_ACTION_SUSPEND);
```

with `CONFIG_PM_DEVICE=y` set. Gate it behind a Kconfig option — e.g.
`project-nrf-template`'s `CONFIG_APP_SUSPEND_CONSOLE` — so it can be
disabled while debugging without editing source, and guard any log-heavy
debug helpers (e.g. `thread_analyzer_print()`) behind the same option,
since they're wasted work once the console they'd print to is suspended.
`project-nrf-thread-switch`'s local `#define SUSPEND_CONSOLE` predates
this convention and is legacy — don't follow it in new code.

## Upstream bugs

If you encounter what appears to be a bug in Zephyr, `sdk-nrf`, or any other
upstream dependency, the preferred path is to:

1. Confirm it is a real upstream bug (not a local misconfiguration).
2. Fix it in the upstream repository.
3. Open a pull request with the fix.

Do **not** work around upstream bugs locally unless a temporary workaround is
unavoidable while the upstream fix is in review. Document any such workaround
clearly and link the upstream PR.
