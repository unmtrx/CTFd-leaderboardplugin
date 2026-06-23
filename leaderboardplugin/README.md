# Leaderboard Plugin

This folder contains a standalone CTFd plugin that replaces the default scoreboard page with a custom leaderboard UI.

## What it does

- Replaces the default `scoreboard.html` with a podium-style leaderboard
- Supports both:
  - `Solo` leaderboard via `?view=users`
  - `Team` leaderboard via `?view=teams`
- Defaults to `Solo`
- Removes dependency on the default scoreboard graph/table UI
- Adds a `/leaderboard` route while also overriding the existing scoreboard endpoint

## Files

- `leaderboardplugin/__init__.py`
  - plugin loader
  - scoreboard route override
  - leaderboard rendering logic
- `leaderboardplugin/templates/scoreboard.html`
  - custom leaderboard template

## Install on another CTFd instance

1. Copy this folder into the target instance:

```bash
cp -R leaderboardplugin /path/to/CTFd/CTFd/plugins/leaderboardplugin
```

2. Restart CTFd.

3. Open:

```text
/leaderboard?view=users
```

or:

```text
/scoreboard?view=users
```

## Notes

- This plugin assumes the target CTFd instance already has:
  - `users.public`
  - `teams.public`
  - base theme templates compatible with `scoreboard.html`
- No asset build step is required because styling is inline in the template.
- If your navbar still links to the old scoreboard route, point it to:

```jinja2
{{ url_for('scoreboard.listing', view='users') }}
```
