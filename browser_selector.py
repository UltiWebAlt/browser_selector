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
            # Although the desktop-entry specification requires URI field codes
            # to be separate arguments, a number of third-party entries use
            # forms such as ``--url=%u``.  Expand those too so selecting a
            # browser never silently drops the link.
            if "%u" in token:
                saw_url_placeholder = True
                if urls:
                    command.append(token.replace("%u", urls[0]))
            elif "%U" in token:
                saw_url_placeholder = True
                if urls:
                    command.extend(token.replace("%U", url) for url in urls)
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
            self.setObjectName("selectorWindow")
            self.setWindowFlags(
                QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint
            )

            button_width = max(84, self.icon_size[0] + 24)
            button_height = max(72, self.icon_size[1] + 24)
            window_width = max(
                160, 32 + len(self.browser_entries) * button_width
                + max(0, len(self.browser_entries) - 1) * 10,
            )

            outer = QtWidgets.QVBoxLayout(self)
            outer.setContentsMargins(0, 0, 0, 0)
            card = QtWidgets.QFrame()
            card.setObjectName("chooserCard")
            outer.addWidget(card)
            layout = QtWidgets.QVBoxLayout(card)
            layout.setContentsMargins(16, 12, 16, 8)
            layout.setSpacing(0)

            has_url = bool(sys.argv[1:])
            if has_url:
                heading = QtWidgets.QHBoxLayout()
                heading.setSpacing(8)
                globe = QtWidgets.QLabel()
                globe.setPixmap(self.globePixmap())
                globe.setFixedSize(16, 16)
                heading.addWidget(globe)
                title = QtWidgets.QLabel("Open link with")
                title.setObjectName("chooserTitle")
                heading.addWidget(title)
                heading.addStretch()
                layout.addLayout(heading)
                layout.addSpacing(10)

                url_box = QtWidgets.QFrame()
                url_box.setObjectName("urlBox")
                url_box.setFixedHeight(32)
                url_layout = QtWidgets.QHBoxLayout(url_box)
                url_layout.setContentsMargins(9, 0, 8, 0)
                url_layout.setSpacing(6)
                url = sys.argv[1]
                url_label = QtWidgets.QLabel()
                url_label.setObjectName("urlLabel")
                url_label.setSizePolicy(
                    QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred
                )
                url_label.setToolTip(url)
                url_font = url_label.font()
                url_font.setPixelSize(12)
                url_font.setUnderline(True)
                url_label.setFont(url_font)
                url_label.setText(
                    url_label.fontMetrics().elidedText(
                        url, QtCore.Qt.ElideRight, window_width - 76
                    )
                )
                url_layout.addWidget(url_label, 1)
                arrow = QtWidgets.QLabel("↗")
                arrow.setObjectName("urlArrow")
                url_layout.addWidget(arrow)
                layout.addWidget(url_box)
                layout.addSpacing(8)

            browsers = QtWidgets.QHBoxLayout()
            browsers.setSpacing(10)
            browsers.addStretch()
            for browser in self.browser_entries:
                entry = DesktopEntry.DesktopEntry(browser)
                icon = QtGui.QIcon()
                icon_path = IconTheme.getIconPath(entry.getIcon())
                if icon_path:
                    icon.addPixmap(QtGui.QPixmap(icon_path))
                name = entry.getName()
                for suffix in (" Web Browser", " Browser"):
                    if name.endswith(suffix):
                        name = name[: -len(suffix)]
                        break
                if name in ("Google Chrome", "Microsoft Edge"):
                    name = name.split(" ", 1)[1]
                button = QtWidgets.QToolButton()
                button_font = button.font()
                button_font.setPixelSize(12)
                button.setFont(button_font)
                button.setText(
                    button.fontMetrics().elidedText(
                        name, QtCore.Qt.ElideRight, button_width - 8
                    )
                )
                button.setIcon(icon)
                button.setIconSize(QtCore.QSize(*self.icon_size))
                button.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
                button.setFixedSize(button_width, button_height)
                button.clicked.connect(partial(self.buttonClicked, browser))
                button.setToolTip(entry.getComment() or entry.getName())
                button.setAccessibleName(entry.getName())
                self.buttons.append(button)
                browsers.addWidget(button)
            browsers.addStretch()
            layout.addLayout(browsers)

            self.setStyleSheet("""
                QWidget#selectorWindow { background: #1c1c1c; }
                QFrame#chooserCard {
                    background: #1c1c1c;
                    border: 1px solid #303030;
                    border-radius: 17px;
                }
                QLabel { color: #f4f4f4; }
                QLabel#chooserTitle { font-size: 13px; font-weight: 600; }
                QFrame#urlBox { background: #151515; border-radius: 8px; }
                QLabel#urlLabel { font-size: 12px; }
                QLabel#urlArrow { color: #a4a4a4; font-size: 12px; }
                QToolButton {
                    background: transparent;
                    color: #f4f4f4;
                    border: 0;
                    border-radius: 9px;
                    font-size: 12px;
                    padding: 0;
                }
                QToolButton:hover, QToolButton:focus { background: #303030; }
                QToolButton:pressed { background: #3c3c3c; }
            """)
            self.setWindowTitle("Browser Selector")
            if self.missing_paths:
                self.setToolTip(
                    "Ignored missing browser entries:\n" + "\n".join(self.missing_paths)
                )

            url_section_height = 20 + 10 + 32 + 8 if has_url else 0
            self.setFixedSize(window_width, 12 + url_section_height + button_height + 8)
            pos = QtGui.QCursor().pos()
            screen = QtGui.QGuiApplication.screenAt(pos) or QtWidgets.QApplication.primaryScreen()
            bounds = screen.availableGeometry()
            x = max(bounds.left(), min(pos.x() - window_width // 2, bounds.right() - window_width + 1))
            y = max(bounds.top(), min(pos.y() - self.height() // 2, bounds.bottom() - self.height() + 1))
            self.move(x, y)
            self.show()

        def keyPressEvent(self, event):
            if event.key() == QtCore.Qt.Key_Escape:
                self.close()
                return
            super().keyPressEvent(event)

        def globePixmap(self):
            pixmap = QtGui.QPixmap(16, 16)
            pixmap.fill(QtCore.Qt.transparent)
            painter = QtGui.QPainter(pixmap)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setPen(QtGui.QPen(QtGui.QColor("#a4a4a4"), 1.2))
            painter.drawEllipse(QtCore.QRectF(1.5, 1.5, 13, 13))
            painter.drawEllipse(QtCore.QRectF(5, 1.5, 6, 13))
            painter.drawLine(QtCore.QPointF(1.5, 8), QtCore.QPointF(14.5, 8))
            painter.end()
            return pixmap

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
