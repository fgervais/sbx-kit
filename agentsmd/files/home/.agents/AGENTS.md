# Agent Instructions

## Authoring Skills & Documentation

- Do not include ephemeral information (versions, dates, transient state) in
  skills or documentation.
- Prefer linking to the source repository where the information can be
  fetched when required, rather than duplicating content that may go stale.

## Code & Text Style

- Aim for 80-100 characters per line in text and code files.

## Embedded Development & Remote/Network Interactions

- Be cautious with iteration loops that involve embedded hardware (flashing,
  resetting, power-cycling) or remote network interactions (APIs, servers,
  wireless connections). Do not brute-force a change-flash-reset or
  retry-on-failure loop.
- Each reset of a device can pass through a transient unsafe hardware
  configuration, or trigger a reconnection (e.g., to a wireless network).
  Rapid disconnect/reconnect cycles can trip protections on the server side,
  making it look like a new bug when there isn't one.
- The same caution applies to remote APIs: repeated fast retries can trigger
  rate limiting or other protective measures on the remote server, leaving
  you unable to debug at all.
- Favor thinking over retrying: design the test that gives the most signal
  from a single attempt rather than looping through many small attempts.
- If failures persist after a reasonable attempt, stop and brainstorm with
  the user instead of continuing to retry.

## Git Workflow

- Try to keep the commit subject line to 50 characters or fewer, and wrap
  the body at 72 characters.
- Prefix the subject line with an appropriate context (e.g., the top-level
  directory or component affected) when it makes sense
  (e.g., `<prefix>: your message here`).
- Commit once a logical unit of work is done. Commit as you go, not all at
  once at the end.
- When refining work that's already committed — adjusting an approach,
  incorporating an idea from elsewhere, fixing something that belongs to
  the same logical unit — create a fixup against the target commit
  (`git commit --fixup=<sha>`) so it sits alongside its target, ready for
  the user to fold in later with `git rebase --autosquash`. This holds
  even when the target is the most recent commit (HEAD): use
  `git commit --fixup`, not `git commit --amend`.
- After writing a fixup, re-read the target commit's message. If anything
  in that message has become inaccurate or misleading because of the
  fixup, use an amend! commit instead.

## Ordering

- When managing a list of items, use alphabetical order when it makes sense.

## Repository Awareness

- When working in a repo, look for skills that may already be available and use
  them where applicable.

## Sandbox Environment

- The agent runs in a sandbox. Only the user can perform actions on the host.
  - If an action needs to be taken on the host, ask the user rather than
    attempting it yourself.
- The agent has both sudo and Docker available in the sandbox and should use
  its judgment to choose whichever is most appropriate for the task at hand.
- When using Docker, reuse a project's existing Dockerfile when present, and
  prefer running images from an official source (e.g., the project's own
  registry, or an image's official vendor/organization) over unverified
  third-party images.
- All network traffic from the sandbox goes through a gateway with network
  filtering. If an external request unexpectedly fails to reach out, ask
  the user to check whether sandbox network filtering is blocking it.
- All outbound TCP through the sandbox proxy — including raw, non-HTTP
  tunnels — is only established end-to-end once the client sends its first
  bytes, so `connect()` succeeds but a read-only client gets zero bytes and
  is dropped after a few seconds of silence (raw socket EOF, or pyserial
  socket disconnected). Always write at least one byte (e.g. a newline)
  right after connecting, then read.
