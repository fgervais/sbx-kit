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
use it?* Keep it short. Anyone who wants deeper detail can clone the repo and
ask an agent.

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
5. **Usage** — the minimal command or steps to get started.
6. **Build** (optional) — include only if building is non-obvious or
   requires special steps.

## What to leave out

- **CLI flags and option tables.** These go stale. Point the user to
  `--help` or the source instead.
- **Internal design docs or architecture diagrams.** Those belong in the
  repo itself, not the README.
- **Version numbers or release history.** Use tags and changelogs for that.
- **Anything the agent can discover by reading the code.** If a curious
  user can just clone and ask, don't duplicate it in the README.

## Editing an existing README

- Read the entire file before making changes, not just the section you
  intend to touch.
- Look for duplicate or redundant information (the same fact stated in
  multiple sections) and consolidate it.

## Tone and style

- Write in plain language; avoid filler phrases ("This project aims to…").
- Use code blocks for every command.
- Prefer links to authoritative sources over copy-pasted content that will
  drift out of sync.
- Aim for 80–100 characters per line in prose.
