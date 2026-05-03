# Reminders

A minimal CLI that fires desktop notifications for YAML-defined reminders. No app, no UI — just files and `notify-send`.

## Installation

**pip / pipx** (recommended):

```sh
pipx install reminders
# or
pip install reminders
```

**From source:**

```sh
pip install git+https://github.com/danisztls/reminders
```

**Arch Linux (AUR):**

```sh
yay -S reminders-git
```

## Setup

On first run, `reminders` auto-creates `$XDG_CONFIG_HOME/reminders/config.yaml` with a default reminders file:

```yaml
# $XDG_CONFIG_HOME/reminders/config.yaml
paths:
  - "~/.config/reminders/reminders.yaml"
```

Add more paths to load reminders from multiple files:

```yaml
paths:
  - "~/.config/reminders/personal.yaml"
  - "~/.config/reminders/work.yaml"
  - "~/notes/reminders.yaml"
```

## Reminder format

Each reminder file is a YAML list. Copy `reminders.template.yaml` from this repo as a starting point.

### Fields

| Field | Required | Description |
|---|---|---|
| `name` | yes | Notification title |
| `desc` | no | Notification body text |
| `next` | yes* | Date to trigger (`YYYY-MM-DD`) |
| `last` | yes* | Date last completed (`YYYY-MM-DD`), used with `freq` |
| `freq` | with `last` | Recurrence interval (e.g. `1d`, `2w`, `3m`, `1y`) |
| `yearly` | yes* | Annual recurrence on a fixed date (`MM-DD`) |
| `monthly` | yes* | Monthly recurrence on a fixed day (`DD`) |
| `early` | no | Fire this long before the due date (same format as `freq`) |

*One of `next`, `last`+`freq`, `yearly`, or `monthly` is required.

**Frequency units:** `d` (day), `w` (week), `m` (month), `y` (year).

### Examples

**One-time reminder** — fires on a specific date:

```yaml
- name: "Dentist appointment"
  desc: "Call to confirm beforehand."
  next: 2026-06-15
```

**One-time with early notification** — fires 3 days before the date:

```yaml
- name: "Passport renewal"
  next: 2026-07-01
  early: 3d
```

**Recurring reminder** — fires when `last + freq` is past today. Update `last` after each completion:

```yaml
- name: "Water the plants"
  last: 2026-04-28
  freq: 1w
```

**Recurring with description and early notification:**

```yaml
- name: "Back up hard drive"
  desc: "Run restic to external drive."
  last: 2026-04-01
  freq: 1m
  early: 2d
```

**Yearly reminder** — fires once a year on a fixed date; notifies up to 7 days after if missed:

```yaml
- name: "Mom's birthday"
  yearly: "06-15"
```

**Yearly with early notification** — fires ahead of the date:

```yaml
- name: "Tax return"
  desc: "Gather documents and file."
  yearly: "04-15"
  early: 14d
```

**Monthly reminder** — fires once a month on a fixed day; notifies up to 7 days after if missed:

```yaml
- name: "Pay rent"
  monthly: "01"
```

**Monthly with early notification:**

```yaml
- name: "Pay rent"
  monthly: "01"
  early: 3d
```

## Usage

```sh
reminders
```

Reminders does not modify your files — after completing a task, update `last` or remove the entry manually.

## Automation

Install the included systemd user units to run reminders hourly in the background:

```sh
cp reminders.service reminders.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now reminders.timer
```

Check status:

```sh
systemctl --user status reminders.timer
journalctl --user -u reminders.service
```

## Requirements

- `notify-send` (provided by `libnotify` on most distros)
- Python 3.11+
