# Reminders

Reminders is a script that reads **reminders** stored in an YAML configuration file and notifies of those that are past date.

I'm writing this because this is an important use case for me and I'm tired of dealing with the usual productivity app and yet another UI. 

## Installation

`pip install reminders`

or

`pip install git+https://github.com/danisztls/reminders`

## Configuration

It expects a configuration file at `$XDG_CONFIG_HOME/reminders/config.yaml` such as:

```yaml
paths:
  - "~/reminders.yml"
```

It supports multiple reminders file with the following structure:

```yaml
- name: ""
  desc: "Notify when next date is past."
  next: 2024-01-30

- name: "Task B"
  desc: "Notify when last date + frequency relative delta is past."
  last: 2024-01-01 
  freq: 1m

```

`freq` support these units: **d** *(day)*, **w** *(week)*, **m** *(month)*, **y** *(year)*.

## Usage

Just run: 

```bash
reminders
```

It can be run periodically in the background so notifications are sent in due time.

It doesn't write to the configuration file so the user have to manually edit it after the task is done.

Currently it supports one method of notiying which is GNOME [libnotify](https://gitlab.gnome.org/GNOME/libnotify).
