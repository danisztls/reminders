# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```sh
# Install dependencies
uv sync

# Run directly
uv run reminders

# Build and install (for local testing)
uv pip install -e .
```

There are no tests in this project.

## Architecture

Single-file Python CLI (`reminders.py`) that reads YAML reminder files and fires `notify-send` desktop notifications for overdue entries.

**Flow:** `main()` loads `$XDG_CONFIG_HOME/reminders/config.yaml` (auto-created on first run), iterates over each path listed there, and for each reminder entry calls `check_reminders()`. An entry triggers a notification if its `next` date is past today, or if `last + freq` (computed via `calc_next_date`) is past today.

**Frequency format:** string like `1d`, `2w`, `3m`, `1y` — parsed in `calc_next_date` using `dateutil.relativedelta`.

**Packaging:** `pyproject.toml` with UV/hatchling; the `dist/arch/` submodule is the AUR package (`reminders-git`). The `reminders.service` and `reminders.timer` are systemd user units for running the tool hourly.
