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

## Module ownership

Board definitions may come from the west module **`zephyr-my-boards`** and
shared code from **`zephyr-mymodule-base`**. Both modules are under our
control but changes to them require a discussion and agreement before
proceeding — do not modify them unilaterally. Raise the need and design the
change collaboratively first.

## Power consumption

Always target the lowest power profile. Do not enable peripherals, clocks, or
subsystems that are not required by the application. Prefer device tree
`status = "disabled"` for unused nodes and avoid Kconfig options that pull in
unnecessary drivers or subsystems.

## Upstream bugs

If you encounter what appears to be a bug in Zephyr, `sdk-nrf`, or any other
upstream dependency, the preferred path is to:

1. Confirm it is a real upstream bug (not a local misconfiguration).
2. Fix it in the upstream repository.
3. Open a pull request with the fix.

Do **not** work around upstream bugs locally unless a temporary workaround is
unavoidable while the upstream fix is in review. Document any such workaround
clearly and link the upstream PR.
