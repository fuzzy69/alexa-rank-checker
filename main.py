# -*- coding: UTF-8 -*-
# !/usr/bin/env python

import sys

from PyQt5 import QtWidgets

from application.mainwindow import MainWindow
from application.conf import __author__, __title__


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName(__author__)
    app.setOrganizationDomain("fuzzy69.com")
    app.setApplicationName(__title__)
    app.setStyleSheet("QStatusBar::item { border: 0px solid black };")
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()
