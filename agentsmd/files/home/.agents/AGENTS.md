# Agent Instructions

## Authoring Skills & Documentation

- Do not include ephemeral information (versions, dates, transient state) in
  skills or documentation.
- Prefer linking to the source repository where the information can be
  fetched when required, rather than duplicating content that may go stale.

## Code & Text Style

- Aim for 80-100 characters per line in text and code files.

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
- The agent has sudo access and can install things in the sandbox.
