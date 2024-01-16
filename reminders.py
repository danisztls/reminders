#!/usr/bin/env python

"""
Trigger notifications for reminders.
"""

__author__  = "Daniel Souza <me@posix.dev.br>"
__license__ = "MIT"

import yaml
import subprocess
import datetime
from pathlib import Path
import os

CONFIG_FILE = Path(os.getenv("XDG_CONFIG_HOME"), "reminders/config.yaml")

def load_config() -> dict:
    with open(CONFIG_FILE, 'r') as config:
        return yaml.safe_load(config)

def read_reminders(file_path: str) -> list:
    with open(file_path, 'r') as file:
        reminders = yaml.safe_load(file)
    return reminders

def send_notification(summary: str, body: str) -> None:
    subprocess.run(['notify-send', summary, body])

def check_reminders(reminders: list) -> None:
    today = datetime.date.today()
    for reminder in reminders:
        reminder_date = datetime.datetime.strptime(reminder['date'], '%y-%m-%d').date()
        if reminder_date <= today:
            summary = reminder['name']
            if reminder.get('description'):
                body = f"{reminder['description']} [{reminder_date}]"
            else:
                body = str(reminder_date)
            send_notification(summary, body)

if __name__ == "__main__":
    config = load_config()
    for path in config['paths']:
        reminders = read_reminders(os.path.expanduser(path))
        check_reminders(reminders)
