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
        if reminder.get('next'):
            next_date = reminder['next'] 
        else:
            last_date = reminder['last']
            next_date = calc_next_date(last_date, reminder['freq'])

        if next_date <= today:
            print(reminder)
            summary = reminder['name']
            if reminder.get('desc'):
                body = f"{reminder['desc']} [{next_date}]"
            else:
                body = str(next_date)
            send_notification(summary, body)

def calc_next_date(last_date: datetime, freq: str) -> datetime:
    freq_unit = freq[-1]
    freq_value = int(freq[0:-1])

    if freq_unit == "d":
        delta = relativedelta(days=+freq_value)
    elif freq_unit == "w":
        delta = relativedelta(weeks=+freq_value)
    elif freq_unit == "m":
        delta = relativedelta(months=+freq_value)
    elif freq_unit == "y":
        delta = relativedelta(years=+freq_value)

    next_date = last_date + delta
    return next_date

def main():
    config = load_config()
    for path in config['paths']:
        reminders = read_reminders(os.path.expanduser(path))
        check_reminders(reminders)

if __name__ == "__main__":
    main()
