---
name: readme
description: >-
  Guidance for authoring README files — concise, purposeful, and
  low-maintenance.
globs:
  - "**/README.md"
---

# Authoring READMEs

A README should answer two questions quickly: *what is this?* and *how do I
use it?* Keep it short while documenting the user-facing workflow accurately.
Anyone who wants deeper implementation detail can clone the repo and ask an
agent.

## Structure

1. **Title + one-liner** — name of the project and a single sentence
   describing its purpose.
2. **Agent-driven subtitle** (if applicable) — for a project built and
   maintained with coding agents, add the italic subtitle
   `*Agent-driven project — built and maintained with coding agents.*`
   right after the title and before the description.
3. **Description** (optional) — two or three sentences if the one-liner
   isn't enough.
4. **Prerequisites** — only list things the user must set up *outside* the
   repo (accounts, secrets, host tools). Omit if there are none.
5. **Usage** — the minimal commands or steps to get started.
6. **Configuration** (optional) — include only user-facing settings or
   environment variables needed to use the project.
7. **Build** (optional) — include only if building is non-obvious or
   requires special steps.

## What to leave out

- **CLI flags and option tables.** These go stale. Point the user to
  `--help` or the source instead.
- **Internal design docs or architecture diagrams.** Those belong in the
  repo itself, not the README.
- **Version numbers or release history.** Use tags and changelogs for that.
- **Implementation details that do not affect users.** Preserve concise,
  user-facing behavior and workflow guidance even when the implementation is
  discoverable from the code.

## Editing an existing README

- Read the entire file before making changes, not just the section you
  intend to touch.
- Look for duplicate or redundant information (the same fact stated in
  multiple sections) and consolidate it.
- Check commands, paths, and configuration examples against the repository
  before keeping or adding them.

## Tone and style

- Write in plain language; avoid filler phrases ("This project aims to…").
- Put commands in fenced code blocks so readers can copy them easily.
- Prefer links to authoritative sources over copy-pasted content that will
  drift out of sync.
- Aim for 80–100 characters per line in prose.
