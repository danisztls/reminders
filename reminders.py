#!/usr/bin/env python

"""
Trigger notifications for reminders.
"""

__author__  = "Daniel Souza <me@posix.dev.br>"
__license__ = "MIT"

import os
import yaml
import subprocess
import datetime
from pathlib import Path
from dateutil.relativedelta import *

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
        last_date = datetime.datetime.strptime(reminder['date'], '%y-%m-%d').date()

        raw_delta = reminder['freq']
        delta_unit = raw_delta[-1]
        delta_value = int(raw_delta[0:-1])

        if delta_unit == "d":
            delta = relativedelta(days=+delta_value)
        elif delta_unit == "w":
            delta = relativedelta(weeks=+delta_value)
        elif delta_unit == "m":
            delta = relativedelta(months=+delta_value)
        elif delta_unit == "y":
            delta = relativedelta(years=+delta_value)

        next_date= last_date + delta

        if next_date <= today:
            print(reminder)
            summary = reminder['name']
            if reminder.get('desc'):
                body = f"{reminder['desc']} [{next_date}]"
            else:
                body = str(next_date)
            send_notification(summary, body)

def main():
    config = load_config()
    for path in config['paths']:
        reminders = read_reminders(os.path.expanduser(path))
        check_reminders(reminders)

if __name__ == "__main__":
    main()
