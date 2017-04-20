# -*- coding: UTF-8 -*-
# !/usr/bin/env python

import os
import webbrowser
from queue import Queue

from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import (Qt, QSettings, QThread, QTimer, pyqtSlot, pyqtSignal)
from PyQt5.QtGui import (QFont, QStandardItem, QStandardItemModel)

from .conf import ROOT
from .defaults import THREADS, TIMEOUT
from .helpers import readTextFile
from .version import __version__

ui = uic.loadUiType(os.path.join(ROOT, "assets", "ui", "mainwindow.ui"))[0]

class MainWindow(QtWidgets.QMainWindow, ui):
    def __init__(self, parent=None, title=""):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle("{} {}".format(title, __version__))
        self.centerWindow()

    def centerWindow(self):
        fg = self.frameGeometry()
        c = QtWidgets.QDesktopWidget().availableGeometry().center()
        fg.moveCenter(c)
        self.move(fg.topLeft())
