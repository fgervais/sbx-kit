---
name: bubbletea
description: >-
  Guide for building terminal UI applications using Bubbletea.
  Use this when asked to create interactive TUI tools in Go.
globs:
  - "**/*.go"
---

# Bubbletea TUI Applications

[Bubbletea](https://github.com/charmbracelet/bubbletea) is a Go framework for
building terminal UIs based on The Elm Architecture (Model, Update, View).

**Base all implementations on the official examples:**
https://github.com/charmbracelet/bubbletea/tree/main/examples

Browse the examples directory to find the closest match to the desired UI,
then adapt it rather than writing from scratch.

## Core pattern

```go
package main

import (
    "fmt"
    "os"

    tea "github.com/charmbracelet/bubbletea"
)

type model struct {
    // your state here
}

func (m model) Init() tea.Cmd {
    return nil
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
    switch msg := msg.(type) {
    case tea.KeyMsg:
        switch msg.String() {
        case "ctrl+c", "q":
            return m, tea.Quit
        }
    }
    return m, nil
}

func (m model) View() string {
    return "Hello from Bubbletea!\n"
}

func main() {
    p := tea.NewProgram(initialModel())
    if _, err := p.Run(); err != nil {
        fmt.Fprintf(os.Stderr, "error: %v\n", err)
        os.Exit(1)
    }
}
```

## Adding the dependency

```bash
go get github.com/charmbracelet/bubbletea
```

## Useful companion libraries

- [`lipgloss`](https://github.com/charmbracelet/lipgloss) — styling and layout
- [`bubbles`](https://github.com/charmbracelet/bubbles) — ready-made components
  (text input, spinner, progress bar, list, table, viewport, …)

```bash
go get github.com/charmbracelet/lipgloss
go get github.com/charmbracelet/bubbles
```

## Key concepts

- **Model** — plain Go struct holding all application state.
- **Init** — returns an optional `tea.Cmd` to run on startup (e.g. a spinner
  tick, an HTTP fetch).
- **Update** — receives a `tea.Msg`, returns an updated model and an optional
  next `tea.Cmd`. Never mutate the model in-place.
- **View** — pure function; returns the full screen as a string on every frame.
- **Commands (`tea.Cmd`)** — functions that run outside the update loop and
  return a `tea.Msg` when done. Use them for I/O, timers, and goroutines.

## Common message types

| Message | Meaning |
|---|---|
| `tea.KeyMsg` | Key press |
| `tea.WindowSizeMsg` | Terminal resized |
| `tea.TickMsg` | Timer fired (from `tea.Tick`) |
| `tea.Cmd` returned by components | Component-internal events |

## Tips

- Call `tea.NewProgram(m, tea.WithAltScreen())` for full-screen apps.
- Use `tea.WithMouseCellMotion()` to enable mouse support.
- Keep `View()` free of side effects — it may be called multiple times per
  update.
- Return `tea.Quit` from `Update` to exit cleanly.
