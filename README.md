# Browser Selector

<img src="assets/png/alt/browser-selector-icon-alt-256.png" alt="Browser Selector alt icon" width="256" height="256" />

Small Linux GUI utility that shows browser icons and opens the clicked browser with the URL(s) passed on the command line.

Original creator: https://www.reddit.com/user/AiwendilH/  
Original thread: https://www.reddit.com/r/linux/comments/2lgokr/looking_for_an_app_that_lets_you_choose_web/

Originally Python 2 + PyQt4 + pyxdg, now ported to Python 3 + PyQt5 + pyxdg, with ongoing Wayland-focused improvements.\
Tested on multiple Linux Mint versions up to 22.3, using X11, and Wayland on Manjaro 26.0.2 / KDE Plasma 6.5.5.

## Requirements

- Linux desktop environment with `.desktop` browser entries
- Python 3.10+

Python dependencies are installed automatically by the install commands below.

## Quick Install (local project clone)

```bash
./install.sh
```

Run:

```bash
~/.local/bin/browser-selector/.venv/bin/browser-selector "https://example.com"
```

`install.sh` copies the script and its virtual environment into
`~/.local/bin/browser-selector/`. It also installs the desktop launcher and
icon automatically.
To skip that step: `SKIP_DESKTOP_SETUP=1 ./install.sh`
The desktop entry points to the installed launcher, so the clone can be moved
or removed after installation.
To remove the desktop launcher and icon later, run
`bash desktop/uninstall_desktop_entry.sh`.

## Alternative Install (recommended for end users)

If you use `pipx`, this keeps dependencies isolated automatically:

```bash
pipx install .
browser-selector "https://example.com"
./desktop/install_desktop_entry.sh
```

## Configuration

On first run, a config file is created at:

`~/.config/browser-selector/config.json`

Example:

```json
{
  "browsers": [
    "/usr/share/applications/firefox.desktop",
    "/usr/share/applications/brave-browser.desktop"
  ],
  "icon_size": [48, 48]
}
```

- `browsers`: list of `.desktop` file paths to show in the selector
- `icon_size`: `[width, height]` in pixels

If a configured `.desktop` file is missing, it is ignored. If all are missing, startup exits with a clear error.

## Troubleshooting

- Missing dependencies error: run `python3 -m pip install PyQt5 pyxdg`
- No usable browser entries: fix the paths in `~/.config/browser-selector/config.json`
- Offline install: preinstall Python packages (`PyQt5`, `pyxdg`) in your environment before running `./install.sh`
