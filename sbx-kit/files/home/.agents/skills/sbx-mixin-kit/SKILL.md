---
name: sbx-mixin-kit
description: >-
  Practical guide for authoring Docker Sandboxes mixin kits (spec.yaml).
  Covers the spec structure, install gotchas, skill delivery,
  and lessons learned from real kit work.
globs:
  - "**/spec.yaml"
  - "**/spec.yml"
---

# Authoring a Docker Sandboxes Mixin Kit

## Install the kit-author skill

The `kit-author` skill from `docker/sbx-kits-contrib` covers the full spec schema,
lifecycle, composition, and distribution. Install it first for detailed reference.

Find it at: https://github.com/docker/sbx-kits-contrib — the skills directory contains
`kit-author` with installation instructions.

## Installing sbx

`sbx` is available inside the sandbox via apt:

```bash
sudo apt-get install -y docker-sbx
```

## Network allow list

- Entries can include a port: `localhost:8000`
- Port-scoped entries are tighter and preferred when the kit only needs one port
- The allow list is **static** — it cannot reference env vars, so if you expose a
  configurable port via an env var, the allow list and the env var default must agree
- To reach a service on the host machine, the agent connects to `host.docker.internal`
  (the DNS name that resolves to the host from inside the container). However, the
  proxy's allow list must use `localhost` — the proxy resolves `host.docker.internal`
  to localhost when evaluating the policy. So: **connect to `host.docker.internal`,
  allow `localhost`**.

## Installing packages

Always run `apt-get update` before `apt-get install` — the sandbox image's package
index may be stale and the package won't be found otherwise:

```yaml
- command: "apt-get update && apt-get install -y my-package"
  user: "0"
```

## Delivering a skill to the sandbox agent

Place the skill file under `files/home/` in the kit — the engine copies it into
`/home/agent/` at kit-apply time:

```
my-kit/
├── spec.yaml
└── files/
    └── home/
        └── .agents/
            └── skills/
                └── my-skill/
                    └── SKILL.md
```

No install command needed — it's purely declarative.

## Writing skills for agents (not humans)

Skills are read by the sandbox agent. Keep this in mind:

- **Don't include host-side setup steps** — the agent cannot run commands on the
  host. If the user needs to do something first, note it as a prerequisite in the
  description but don't write it as an actionable step for the agent.
- **Don't hardcode values the agent reads from env vars** — if the agent uses
  `$MY_VAR`, the skill should reference `$MY_VAR` by name, not its default value.
  Hardcoded values go stale and create a maintenance burden.
- **Write for scripted use** — agents don't use interactive tools (no `picocom`,
  no `screen`). Prefer Python snippets, shell one-liners, or file I/O patterns.

## Kit name vs skill name

- **Kit name** (`name:` in spec.yaml) — describes what the mixin *does* mechanically
- **Skill name** — describes what the agent *can now do*

Example: kit `serial-proxy` delivers skill `serial-console`.

## Iteration workflow

Validate early and often — it catches structural errors before the user runs anything:

```bash
sbx kit validate ./my-kit/
```

Sandbox lifecycle (run, exec, rm) is managed by the user, not the agent. If validation
passes, hand off to the user for runtime testing.
