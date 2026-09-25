# Homelab wiki monitor

Ryan Server runs `wiki-monitor.timer` every 15 minutes, with up to 30 seconds
of jitter. GitHub Actions builds and deploys the site through `publish-wiki.yml`
(Publish Wiki), restored from the last successful deployment at `1b6ccc9`.
Its fallback schedule runs once daily at 10:00 UTC.

The Python standard-library script reads the live `source-revisions.json`, gets
the current repository commit, reads `.gitmodules` at that commit, and resolves
the configured upstream branches. It dispatches only when a revision differs
and no Publish Wiki workflow for the current repository revision is active.
Dispatches send only `ref=main`; the workflow always builds and deploys.
Change detection happens entirely in the homelab monitor; the daily Actions run
is a dumb fallback.

The monitor has no local success marker. Only a successful deployment updates
the live marker; failed builds and network errors are retried at the next check.
Malformed markers and API failures fail the check rather than forcing builds.
Systemd prevents overlapping local checks, catches up once after downtime, and
records stdout/stderr in the journal. There are no inbound ports or dependencies
beyond Python 3.9+ and systemd with LoadCredential support.

## Install

Install `wiki_monitor.py` root-owned at `/opt/wiki-monitor/wiki_monitor.py`, and
the two unit files at `/etc/systemd/system/`. Store a fine-grained GitHub token
at `/etc/wiki-monitor/github-token`, owned by root with mode 0600, inside a
root-owned 0700 directory. Select only `ryan-reid/BT-BKDiff`, with repository
Actions read/write permission. Public repository metadata can be read with this
token. Never commit the token or put it in command arguments.

The service uses a dynamic unprivileged user and systemd credentials; it cannot
write to the application or credential source files. After installing:

```sh
sudo systemd-analyze verify /etc/systemd/system/wiki-monitor.service /etc/systemd/system/wiki-monitor.timer
sudo python3 /opt/wiki-monitor/wiki_monitor.py --token-file /etc/wiki-monitor/github-token --dry-run
sudo systemctl daemon-reload
sudo systemctl start wiki-monitor.service
sudo systemctl enable --now wiki-monitor.timer
```

## Operate

```sh
systemctl list-timers wiki-monitor.timer
systemctl status wiki-monitor.service wiki-monitor.timer
journalctl -u wiki-monitor.service --since today
sudo systemctl start wiki-monitor.service
```

Rotate the credential before its expiration; systemd loads it anew for each
invocation. HTTP 401/403 errors require checking token validity, permissions,
and rate limits. Errors are logged locally; this service does not send alerts.
Disable with `sudo systemctl disable --now wiki-monitor.timer`; the GitHub
schedule remains available. Back up existing installed files before updates.
