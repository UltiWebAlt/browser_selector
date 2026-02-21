#!/usr/bin/env python3
"""
Original creator: https://www.reddit.com/user/AiwendilH/
https://www.reddit.com/r/linux/comments/2lgokr/looking_for_an_app_that_lets_you_choose_web/

Requires Python 3, pyqt5 and pyxdg. Original was Python 2, pyqt4 and pyxdg.
I ported it to Python 3 and relevant dependencies.

This has been tested and used on both Wayland and x11 without any issues.
It should work on any Linux desktop environment that supports .desktop files
and has the required dependencies installed.
"""

import importlib
import json
import os
import shlex
import subprocess
import sys
from functools import partial
from pathlib import Path

DEFAULT_BROWSERS = [
    "/usr/share/applications/brave-browser.desktop",
    "/usr/share/applications/microsoft-edge.desktop",
    "/usr/share/applications/vivaldi-stable.desktop",
    "/usr/share/applications/opera.desktop",
    "/usr/share/applications/firefox.desktop",
]
DEFAULT_ICON_SIZE = [48, 48]
CONFIG_PATH = (
    Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    / "browser-selector"
    / "config.json"
)
REQUIRED_MODULES = [("PyQt5", "PyQt5"), ("xdg", "pyxdg")]


def ensure_default_config(config_path):
    if config_path.exists():
        return
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w", encoding="utf-8") as config_file:
        json.dump(
            {"browsers": DEFAULT_BROWSERS, "icon_size": DEFAULT_ICON_SIZE},
            config_file,
            indent=2,
        )
        config_file.write("\n")


def load_config(config_path):
    ensure_default_config(config_path)
    with config_path.open("r", encoding="utf-8") as config_file:
        config_data = json.load(config_file)
    browsers = config_data.get("browsers", DEFAULT_BROWSERS)
    icon_size = config_data.get("icon_size", DEFAULT_ICON_SIZE)
    if (
        not isinstance(icon_size, list)
        or len(icon_size) != 2
        or not all(isinstance(value, int) and value > 0 for value in icon_size)
    ):
        raise ValueError(
            f"Invalid icon_size in {config_path}. Expected two positive integers."
        )
    if not isinstance(browsers, list) or not all(isinstance(path, str) for path in browsers):
        raise ValueError(f"Invalid browsers list in {config_path}. Expected a list of paths.")
    return browsers, icon_size


def runtime_dependency_errors():
    missing = []
    for module_name, package_name in REQUIRED_MODULES:
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError:
            missing.append(package_name)
    if missing:
        missing_deps = ", ".join(sorted(set(missing)))
        return (
            "Missing dependencies: "
            f"{missing_deps}\nInstall with: python3 -m pip install {missing_deps}"
        )
    return None


def resolve_browser_entries(browser_paths):
    valid_entries = []
    missing_paths = []
    for browser_path in browser_paths:
        if Path(browser_path).is_file():
            valid_entries.append(browser_path)
        else:
            missing_paths.append(browser_path)
    if not valid_entries:
        missing_text = "\n".join(missing_paths) if missing_paths else "(none configured)"
        raise RuntimeError(
            "No usable browser desktop entries found.\n"
            "Configure valid .desktop file paths in:\n"
            f"{CONFIG_PATH}\n\nMissing paths:\n{missing_text}"
        )
    return valid_entries, missing_paths


def build_exec_command(exec_template, urls):
    command = []
    saw_url_placeholder = False
    for token in shlex.split(exec_template):
        if token == "%u":
            saw_url_placeholder = True
            if urls:
                command.append(urls[0])
        elif token == "%U":
            saw_url_placeholder = True
            command.extend(urls)
        elif token in ("%f", "%F", "%d", "%D", "%n", "%N", "%i", "%c", "%k", "%v", "%m"):
            continue
        elif token == "%%":
            command.append("%")
        elif token.startswith("%"):
            continue
        else:
            command.append(token)
    if urls and not saw_url_placeholder:
        command.extend(urls)
    return command


def build_selector_class(QtCore, QtGui, QtWidgets, DesktopEntry, IconTheme):
    class Selector(QtWidgets.QWidget):
        def __init__(self, browser_entries, icon_size, missing_paths):
            super(Selector, self).__init__()
            self.browser_entries = browser_entries
            self.icon_size = icon_size
            self.missing_paths = missing_paths
            self.buttons = []
            self.setupWindow()

        def setupWindow(self):
            # create the buttons for the browsers
            for browser in self.browser_entries:
                icon = QtGui.QIcon()
                # get the icon from the desktop file
                icon_path = IconTheme.getIconPath(DesktopEntry.DesktopEntry(browser).getIcon())
                if icon_path:
                    icon.addPixmap(QtGui.QPixmap(icon_path))
                self.buttons += [QtWidgets.QPushButton("")]
                self.buttons[-1].setIcon(icon)
                self.buttons[-1].setIconSize(QtCore.QSize(self.icon_size[0], self.icon_size[1]))
                self.buttons[-1].clicked.connect(partial(self.buttonClicked, browser))
                # set the tooltip to the comment of the desktop entry
                self.buttons[-1].setToolTip(DesktopEntry.DesktopEntry(browser).getComment())
            # and the layout
            hbox = QtWidgets.QHBoxLayout()
            for button in self.buttons:
                hbox.addWidget(button)
            self.setLayout(hbox)
            self.setWindowTitle("Browser Selector")
            if self.missing_paths:
                self.setToolTip(
                    "Ignored missing browser entries:\n" + "\n".join(self.missing_paths)
                )
            # in case someone dislikes the default X icon...just set whatever icon you want here
            #self.setWindowIcon(QtGui.QIcon('whatever.png'))
            # move the window to the cursor
            pos = QtGui.QCursor().pos()
            self.move(pos.x() - (self.icon_size[0] // 2), pos.y() - self.icon_size[1] // 2)
            self.show()

        def buttonClicked(self, browser):
            urls = sys.argv[1:]
            exec_name = DesktopEntry.DesktopEntry(browser).getExec()
            command = build_exec_command(exec_name, urls)
            if not command:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Browser Selector Error",
                    f"Could not build launch command from desktop entry:\n{browser}",
                )
                return
            subprocess.Popen(command, start_new_session=True)
            sys.exit()

    return Selector


def main():
    dependency_error = runtime_dependency_errors()
    if dependency_error:
        print(dependency_error, file=sys.stderr)
        return 1

    from PyQt5 import QtCore as _QtCore
    from PyQt5 import QtGui as _QtGui
    from PyQt5 import QtWidgets as _QtWidgets
    from xdg import DesktopEntry as _DesktopEntry
    from xdg import IconTheme as _IconTheme

    try:
        browser_entries_config, icon_size = load_config(CONFIG_PATH)
        browser_entries, missing_paths = resolve_browser_entries(browser_entries_config)
    except (OSError, ValueError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 1

    selector_class = build_selector_class(
        _QtCore, _QtGui, _QtWidgets, _DesktopEntry, _IconTheme
    )

    app = _QtWidgets.QApplication(sys.argv)
    selector_class(browser_entries, icon_size, missing_paths)
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
