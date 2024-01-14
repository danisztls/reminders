#!/usr/bin/env python

"""
Trigger notifications for reminders.
"""

__author__  = "Daniel Souza <me@posix.dev.br>"
__license__ = "MIT"

import yaml
import subprocess
import datetime

def read_reminders(file_path):
    with open(file_path, 'r') as file:
        reminders = yaml.safe_load(file)
    return reminders

"""
Example of 'reminders.yaml':

```yaml
reminders:
  - name: "Water Plants"
    description: "Lorem Ipsum dolor sit amet"
    date: 24-01-10 # last time it was done
    every: 1d # frequency of activity
```
"""

def send_notification(title, message):
    subprocess.run(['notify-send', title, message])

def check_reminders(reminders):
    today = datetime.date.today()
    for reminder in reminders:
        reminder_date = datetime.datetime.strptime(reminder['date'], '%d-%m-%y').date()
        if reminder_date == today:
            send_notification(reminder['name'], reminder['description'])

# TODO: Send notifications to desktop via the command `notify-send`

if __name__ == "__main__":
    # TODO: Read file from CLI param.
    reminders = read_reminders('reminders.yaml')
    check_reminders(reminders['reminders'])
