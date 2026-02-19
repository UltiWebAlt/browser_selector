#!/usr/bin/python

# Original creator: https://www.reddit.com/user/AiwendilH/
# Taken from https://www.reddit.com/r/linux/comments/2lgokr/looking_for_an_app_that_lets_you_choose_web/

# Requires Python 3, pyqt5 and pyxdg. Original was Python 2, pyqt4 and pyxdg. I ported it to more current
# versions of Python and the other dependencies.

browsers = ["/usr/share/applications/brave-browser.desktop", "/usr/share/applications/microsoft-edge.desktop", "/usr/share/applications/vivaldi-stable.desktop", "/usr/share/applications/google-chrome.desktop", "/usr/share/applications/microsoft-edge-dev.desktop", "/usr/share/applications/firefox.desktop"]
iconSize = [48,48]

import sys
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from xdg import DesktopEntry
from xdg import IconTheme
from functools import partial
import os

class Selector(QtWidgets.QWidget):
    def __init__(self):
        super(Selector, self).__init__()
        self.buttons=[]
        self.setupWindow()

    def setupWindow(self):
        # create the buttons for the browsers
        for browser in browsers:
            icon = QtGui.QIcon()
            # get the icon from th desktop file
            icon.addPixmap(QtGui.QPixmap(IconTheme.getIconPath(DesktopEntry.DesktopEntry(browser).getIcon())))
            self.buttons += [QtWidgets.QPushButton("")]
            self.buttons[-1].setIcon(icon)
            self.buttons[-1].setIconSize(QtCore.QSize(iconSize[0],iconSize[1]))
            self.buttons[-1].clicked.connect(partial(self.buttonClicked, browser))
            ## set the tooltip to the comment of the desktop entry
            self.buttons[-1].setToolTip(DesktopEntry.DesktopEntry(browser).getComment())
        #and the layout
        hbox = QtWidgets.QHBoxLayout()
        for button in self.buttons:
            hbox.addWidget(button)
        self.setLayout(hbox)
        self.setWindowTitle("Browser Selector")
        # in case someone dislikes the default X icon...just set whatever icon you want here
        #self.setWindowIcon(QtGui.QIcon('whatever.png'))
        # move the window to the cursor
        pos = QtGui.QCursor().pos()
        self.move(pos.x()-(iconSize[0]/2), pos.y()-iconSize[1]/2)
        self.show()
    def buttonClicked(self, browser):
        #ugly, wrong...and hacky...but works for me and I am too lazy to do it right
        urls = ""
        for url in sys.argv[1:]:
            # if url != "":
            urls += " '" + url + "'"
        execName=DesktopEntry.DesktopEntry(browser).getExec().replace("%U", urls)
        os.system(execName + " &")
        sys.exit()

def main():
    app = QtWidgets.QApplication(sys.argv)

    sel=Selector()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

