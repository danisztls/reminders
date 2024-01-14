# Reminders

Reminders is a CLI tool that reads **reminders** stored in an YAML configuration file and notifies of those that are past date.
It can be run periodically like in a Systemd service so notifications can be received in due time.
It doesn't write to the configuration file so the user have to manually edit after the task is done.
I'm writing this because this is an important use case for me (and probably for everyone) and I'm tired of dealing with the usual productivity app.
