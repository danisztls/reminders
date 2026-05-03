#!/usr/bin/env python

"""
Trigger notifications for reminders.
"""

__author__  = "Daniel Souza <me@posix.dev.br>"

import os
import re
import json
import argparse
import unicodedata
import yaml
import subprocess
import datetime
from pathlib import Path
from dateutil.relativedelta import *
from rich.console import Console
from rich.table import Table
from rich import box

CONFIG_FILE = Path(os.getenv("XDG_CONFIG_HOME"), "reminders/config.yaml")
DATA_DIR = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local/share"), "reminders")
STATE_FILE = DATA_DIR / "state.json"
TODAY = datetime.date.today()
NOW = datetime.datetime.now()

def load_config() -> dict:
    with open(CONFIG_FILE, 'r') as config:
        return yaml.safe_load(config)

def create_config() -> None:
    config_dir = os.path.dirname(CONFIG_FILE)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    reminders_file = Path(config_dir, "reminders.yaml")

    default_config = f'''
paths:
  - \"{reminders_file}"
    '''

    with open(CONFIG_FILE, 'w') as f:
        f.write(default_config)

    default_reminders = f'''
- name: "Example Reminder"\n
  desc: "This is an example. Edit configuration at {config_dir}."
  next: {TODAY.strftime("%Y-%m-%d")} 
  last:
  freq:
    '''

    with open(reminders_file, 'w') as f:
        f.write(default_reminders)

def slugify(name: str) -> str:
    slug = unicodedata.normalize('NFD', name.lower()).encode('ascii', 'ignore').decode('ascii')
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')

def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    with open(STATE_FILE, 'r') as f:
        raw = json.load(f)
    state = {}
    for k, v in raw.items():
        if isinstance(v, dict):
            state[k] = {
                'last_notified': datetime.datetime.fromisoformat(v['last_notified']),
                'target_date': v['target_date'],
            }
    return state

def save_state(state: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(
            {k: {'last_notified': v['last_notified'].isoformat(), 'target_date': v['target_date']}
             for k, v in state.items()},
            f,
        )

def _freq_to_days(freq: str) -> float:
    unit, value = freq[-1], int(freq[:-1])
    return {'h': value / 24, 'd': value, 'w': value * 7, 'm': value * 30, 'y': value * 365}[unit]

def calc_cooldown(reminder: dict) -> relativedelta:
    if reminder.get('freq'):
        days = _freq_to_days(reminder['freq'])
        if days < 1:
            return relativedelta(hours=1)
        if days < 7:
            return relativedelta(days=1)
        if days < 30:
            return relativedelta(weeks=1)
        return relativedelta(months=1)
    next_val = reminder.get('next')
    if isinstance(next_val, datetime.datetime):
        return relativedelta(hours=1)
    if isinstance(next_val, str):
        if 'T' in next_val:
            return relativedelta(hours=1)
        parts = next_val.split('-')
        if len(parts) == 1:
            return relativedelta(months=1)
        if len(parts) == 2:
            return relativedelta(weeks=1)
    return relativedelta(days=1)

def _as_datetime(d) -> datetime.datetime:
    if isinstance(d, datetime.datetime):
        return d
    return datetime.datetime(d.year, d.month, d.day)

def read_reminders(file_path: str) -> list:
    with open(file_path, 'r') as file:
        reminders = yaml.safe_load(file)
    return reminders

def send_notification(summary: str, body: str) -> None:
    subprocess.run(['notify-send', summary, body])

def _month_date(year: int, month: int, day: int) -> datetime.date:
    while True:
        try:
            return datetime.date(year, month, day)
        except ValueError:
            month += 1
            if month > 12:
                month, year = 1, year + 1

def get_trigger_date(reminder: dict):
    if reminder.get('monthly'):
        day = int(reminder['monthly'])
        target_date = _month_date(TODAY.year, TODAY.month, day)
        if TODAY > target_date + datetime.timedelta(days=7):
            next_m = target_date.month % 12 + 1
            next_y = target_date.year + (1 if target_date.month == 12 else 0)
            target_date = _month_date(next_y, next_m, day)
        trigger_date = target_date
        if reminder.get('early'):
            trigger_date = target_date - parse_freq(reminder['early'])
        return trigger_date, target_date

    if reminder.get('yearly'):
        month, day = map(int, reminder['yearly'].split('-'))
        target_date = datetime.date(TODAY.year, month, day)
        if TODAY > target_date + datetime.timedelta(days=7):
            target_date = datetime.date(TODAY.year + 1, month, day)
        trigger_date = target_date
        if reminder.get('early'):
            trigger_date = target_date - parse_freq(reminder['early'])
        return trigger_date, target_date

    if reminder.get('next'):
        next_date = reminder['next']
    elif reminder.get('last'):
        next_date = calc_next_date(reminder['last'], reminder['freq'])
    else:
        return None, None
    trigger_date = next_date
    if reminder.get('early'):
        trigger_date = _as_datetime(next_date) - parse_freq(reminder['early'])
    return trigger_date, next_date

def check_reminders(reminders: list, state: dict) -> None:
    for reminder in reminders:
        trigger_date, next_date = get_trigger_date(reminder)
        if trigger_date is None:
            continue

        if _as_datetime(trigger_date) <= NOW:
            name = reminder['name']
            reminder_id = slugify(name)
            entry = state.get(reminder_id)
            last_notified = entry['last_notified'] if entry else None
            if reminder.get('yearly') or reminder.get('monthly'):
                if entry and entry['target_date'] == str(next_date):
                    continue
            elif last_notified and last_notified + calc_cooldown(reminder) > NOW:
                continue

            target_date = str(next_date)
            is_late = entry and entry['target_date'] == target_date
            late_tag = ' <span foreground="#e06c75">[LATE]</span>' if is_late else ''

            summary = name
            if reminder.get('desc'):
                body = f"{reminder['desc']} [{next_date}]{late_tag}"
            else:
                body = f"{next_date}{late_tag}"
            send_notification(summary, body)
            state[reminder_id] = {'last_notified': NOW, 'target_date': target_date}

def parse_freq(freq: str) -> relativedelta:
    freq_unit = freq[-1]
    freq_value = int(freq[0:-1])

    if freq_unit == "h":
        return relativedelta(hours=+freq_value)
    elif freq_unit == "d":
        return relativedelta(days=+freq_value)
    elif freq_unit == "w":
        return relativedelta(weeks=+freq_value)
    elif freq_unit == "m":
        return relativedelta(months=+freq_value)
    elif freq_unit == "y":
        return relativedelta(years=+freq_value)

def calc_next_date(last_date: datetime, freq: str) -> datetime:
    return last_date + parse_freq(freq)

def print_summary(config: dict) -> None:
    console = Console()
    SOON_HORIZON = datetime.timedelta(days=7)

    late, soon, future = [], [], []

    for path in config['paths']:
        reminders = read_reminders(os.path.expanduser(path))
        for reminder in reminders:
            trigger_date, next_date = get_trigger_date(reminder)
            if trigger_date is None:
                continue
            entry = {
                'name': reminder['name'],
                'desc': reminder.get('desc', ''),
                'trigger_date': _as_datetime(trigger_date),
                'next_date': next_date,
            }
            if entry['trigger_date'] <= NOW:
                late.append(entry)
            elif entry['trigger_date'] <= NOW + SOON_HORIZON:
                soon.append(entry)
            else:
                future.append(entry)

    for group in (late, soon, future):
        group.sort(key=lambda e: e['trigger_date'])

    def make_table(entries: list, color: str, label: str) -> None:
        if not entries:
            return
        has_desc = any(e['desc'] for e in entries)
        table = Table(
            box=box.SIMPLE,
            show_header=False,
            pad_edge=False,
            title=f"[bold {color}]{label} ({len(entries)})[/]",
            title_justify="left",
        )
        table.add_column("date", style=color, no_wrap=True)
        table.add_column("name", style="bold")
        if has_desc:
            table.add_column("desc", style="dim")
        for e in entries:
            date_str = str(e['next_date'])
            row = [date_str, e['name']]
            if has_desc:
                row.append(e['desc'])
            table.add_row(*row)
        console.print(table)

    make_table(late, "red", "Late")
    make_table(soon, "yellow", "Soon")
    make_table(future, "white", "Future")

def main():
    parser = argparse.ArgumentParser(description="Trigger notifications for reminders.")
    parser.add_argument('--summary', action='store_true', help="Pretty-print a summary of all reminders.")
    args = parser.parse_args()

    if not os.path.isfile(CONFIG_FILE):
        create_config()

    config = load_config()

    if args.summary:
        print_summary(config)
        return

    state = load_state()

    for path in config['paths']:
        reminders = read_reminders(os.path.expanduser(path))
        check_reminders(reminders, state)

    save_state(state)

if __name__ == "__main__":
    main()
