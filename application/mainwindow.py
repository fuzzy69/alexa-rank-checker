# -*- coding: UTF-8 -*-
# !/usr/bin/env python

import csv
import json
import operator
import os
import platform
import webbrowser
from queue import Queue

from PyQt5 import (
    uic, QtWidgets
    )
from PyQt5.QtCore import (
    Qt, QSettings, QThread, QTimer, pyqtSlot, pyqtSignal, QT_VERSION_STR,
    PYQT_VERSION_STR
    )
from PyQt5.QtGui import (
    QFont, QStandardItem, QStandardItemModel
    )

from .conf import __author__, __title__, __description__, ROOT
from .defaults import DELAY, THREADS, TIMEOUT
from .helpers import readTextFile
from .utils import check_alexa, split_list
from .version import __version__
from .workers import CheckAlexaWorker, MyThread

ui = uic.loadUiType(os.path.join(ROOT, "assets", "ui", "mainwindow.ui"))[0]

MAX_RECENT_FILES = 5

class MainWindow(QtWidgets.QMainWindow, ui):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle("{} - {}".format(__title__, __version__))
        self._settingsFile = os.path.join(ROOT, "data", "settings.ini")
        self._threads = []
        self._workers = []
        self._progressDone = 0
        self._progressTotal = 0
        self._recentFiles = []
        self._recentFilesActions = []
        self.labelActiveThreads = QtWidgets.QLabel("Active threads: 0")
        self.statusbar.addPermanentWidget(self.labelActiveThreads)
        self.sitesModel = QStandardItemModel()
        self.sitesModel.setHorizontalHeaderLabels(["URL", "Rank", "Status"])
        self.sitesTableView.setModel(self.sitesModel)
        self.actionExport_results.triggered.connect(self.exportResults)
        self.actionQuit.triggered.connect(lambda: QtWidgets.QApplication.quit())
        self.actionAbout.triggered.connect(self.helpAbout)
        self.actionImport_URLs.triggered.connect(self.importUrls)
        self.actionClear_table.triggered.connect(self.clearTable)
        self.actionClear_Recent_Files.triggered.connect(self.clearRecentFiles)
        self.sitesTableView.doubleClicked.connect(self.sitesTableView_doubleClicked)
        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)
        self.resizeEvent = self.onResize
        self.closeEvent = self.onClose
        self.showEvent = self.onShow
        self.loadSettings()
        self.centerWindow()
        self.timerPulse = QTimer(self)
        self.timerPulse.timeout.connect(self.pulse)
        self.timerPulse.start(1000)
        self._boldFont = QFont()
        self._boldFont.setBold(True)
        for i in range(MAX_RECENT_FILES):
            self._recentFilesActions.append(QtWidgets.QAction(self))
            self._recentFilesActions[i].triggered.connect(self.openRecentFile)
            if i < len(self._recentFiles):
                if not self.actionClear_Recent_Files.isEnabled():
                    self.actionClear_Recent_Files.setEnabled(True)
                self._recentFilesActions[i].setData(self._recentFiles[i])
                self._recentFilesActions[i].setText(self._recentFiles[i])
                self._recentFilesActions[i].setVisible(True)
            else:
                self._recentFilesActions[i].setVisible(False)
            self.menuRecent_Files.addAction(self._recentFilesActions[i])
        self.updateRecentFilesActions()

    def centerWindow(self):
        fg = self.frameGeometry()
        c = QtWidgets.QDesktopWidget().availableGeometry().center()
        fg.moveCenter(c)
        self.move(fg.topLeft())

    def loadSettings(self):
        if os.path.isfile(self._settingsFile):
            settings = QSettings(self._settingsFile, QSettings.IniFormat)
            self.restoreGeometry(settings.value("geometry", ''))
            self.restoreState(settings.value("windowState", ''))
            # self._tableViewWidth = int(settings.value("tableViewWidth", ''))
            self.threadsSpin.setValue(settings.value("threadsCount", THREADS, type=int))
            self.timeoutSpin.setValue(settings.value("timeoutSpin", TIMEOUT, type=int))
            self._recentFiles = settings.value("recentFiles", [], type=str)

    def saveSettings(self):
        settings = QSettings(self._settingsFile, QSettings.IniFormat)
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        # settings.setValue("tableViewWidth", self.sitesTableView.frameGeometry().width())
        settings.setValue("threadsCount", self.threadsSpin.value())
        settings.setValue("timeout", self.timeoutSpin.value())
        settings.setValue("recentFiles", self._recentFiles)

    def onResize(self, event):
        self.resizeTableColumns()
        QtWidgets.QMainWindow.resizeEvent(self, event)

    def onClose(self, event):
        self.saveSettings()
        QtWidgets.QMainWindow.closeEvent(self, event)

    def onShow(self, event):
        self.resizeTableColumns()
        QtWidgets.QMainWindow.showEvent(self, event)

    def resizeTableColumns(self):
        self.sitesTableView.setColumnWidth(0, int(self.sitesTableView.frameGeometry().width() * 0.6))
        self.sitesTableView.setColumnWidth(1, int(self.sitesTableView.frameGeometry().width() * 0.1))

    def importUrls(self):
        filePath, fileType = QtWidgets.QFileDialog.getOpenFileName(self, "Import URLs", filter="Text files (*.txt)")
        if filePath:
            text = readTextFile(filePath)
            for url in text.strip().splitlines():
                rankCell = QStandardItem("")
                rankCell.setTextAlignment(Qt.AlignCenter)
                self.sitesModel.appendRow([QStandardItem(url), rankCell,QStandardItem("")])
            self.updateRecentFiles(filePath)

    def sitesTableView_doubleClicked(self, modelIndex):
        model = self.sitesModel
        row = modelIndex.row()
        url = model.data(model.index(row, 0))
        webbrowser.open(url)

    def resetTable(self):
        model = self.sitesModel
        for i in range(model.rowCount()):
            model.setData(model.index(i, 1), "")
            model.setData(model.index(i, 2), "")

    def clearTable(self):
        self.tableRemoveAllRows(self.sitesModel)

    def tableRemoveAllRows(self, model):
        for i in reversed(range(model.rowCount())):
            model.removeRow(i)

    def pulse(self):
        self.labelActiveThreads.setText("Active threads: {}".format(MyThread.activeCount))
        if MyThread.activeCount == 0:
            # if not self.sitesTableView.isSortingEnabled():
                # self.sitesTableView.setSortingEnabled(True)
            if not self.startButton.isEnabled():
                self.startButton.setEnabled(True)
            if self.stopButton.isEnabled():
                self.stopButton.setEnabled(False)
        # else:
        #     if self.sitesTableView.isSortingEnabled():
        #         self.sitesTableView.setSortingEnabled(False)

    def updateRecentFiles(self, filePath):
        if filePath not in self._recentFiles:
            self._recentFiles.insert(0, filePath)
        if len(self._recentFiles) > MAX_RECENT_FILES:
            self._recentFiles.pop()
        self.updateRecentFilesActions()
        if not self.actionClear_Recent_Files.isEnabled():
            self.actionClear_Recent_Files.setEnabled(True)

    def updateRecentFilesActions(self):
        for i in range(MAX_RECENT_FILES):
            if i < len(self._recentFiles):
                self._recentFilesActions[i].setText(self._recentFiles[i])
                self._recentFilesActions[i].setData(self._recentFiles[i])
                self._recentFilesActions[i].setVisible(True)
            else:
                self._recentFilesActions[i].setVisible(False)

    def openRecentFile(self):
        filePath = str(self.sender().data())
        if os.path.exists(filePath):
            text = readTextFile(filePath)
            for url in text.strip().splitlines():
                rankCell = QStandardItem("")
                rankCell.setTextAlignment(Qt.AlignCenter)
                self.sitesModel.appendRow([QStandardItem(url), rankCell,QStandardItem("")])

    def clearRecentFiles(self):
        self._recentFiles = []
        self.updateRecentFilesActions()
        self.actionClear_Recent_Files.setEnabled(False)

    @pyqtSlot()
    def start(self):
        self.resetTable()
        model = self.sitesModel
        queues = split_list(range(self.sitesModel.rowCount()), self.threadsSpin.value())
        self._progressTotal = self.sitesModel.rowCount()
        self._progressDone = 0
        self._threads = []
        self._workers = []
        for i, rows in enumerate(queues):
            self._threads.append(MyThread())
            queue = Queue()
            for row in rows:
                url = model.data(model.index(row, 0))
                queue.put((row, url))
            self._workers.append(CheckAlexaWorker(check_alexa, delay=self.delaySpin.value(), timeout=self.timeoutSpin.value(), queue=queue))
            self._workers[i].moveToThread(self._threads[i])
            self._threads[i].started.connect(self._workers[i].start)
            self._threads[i].finished.connect(self._threads[i].deleteLater)
            self._workers[i].status.connect(self.onStatus)
            self._workers[i].result.connect(self.onResult)
            self._workers[i].finished.connect(self._threads[i].quit)
            self._workers[i].finished.connect(self._workers[i].deleteLater)
        for i in range(self.threadsSpin.value()):
            self._threads[i].start()
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)

    @pyqtSlot()
    def stop(self):
        for i, _ in enumerate(self._workers):
            self._workers[i]._running = False

    @pyqtSlot(tuple)
    def onStatus(self, tuple_):
        i, status = tuple_
        self.sitesModel.setData(self.sitesModel.index(i, 2), status)

    @pyqtSlot(object)
    def onResult(self, result):
        self.sitesModel.item(result["row"], 1).setFont(self._boldFont)
        if result["status"]:
            self.sitesModel.setData(self.sitesModel.index(result["row"], 1), result["rank"])
            self.sitesModel.item(result["row"], 1).setForeground(Qt.green)
        elif result["status"] is None:
            self.sitesModel.setData(self.sitesModel.index(result["row"], 1), "No data")
        else:
            self.sitesModel.setData(self.sitesModel.index(result["row"], 1), "Fail")
            self.sitesModel.item(result["row"], 1).setForeground(Qt.red)
        self._progressDone += 1
        self.progressBar.setValue(int(float(self._progressDone) / self._progressTotal * 100))

    def helpAbout(self):
        QtWidgets.QMessageBox.about(self, "About {}".format(__title__),
            """<b>{} v{}</b>
            <p>All rights reserved.
            <p>{}
            <p>Python {} - Qt {} - PyQt {} on {}""".format(
                __title__, __version__, __description__,
                platform.python_version(), QT_VERSION_STR, PYQT_VERSION_STR,
                platform.system())
        )

    def exportResults(self):
        filePath, fileType = QtWidgets.QFileDialog.getSaveFileName(self, "Export results", "/mnt/ramdisk/results", filter="CSV files (*.csv);;JSON files (*.json)")
        data = []
        model = self.sitesModel
        for i in range(model.rowCount()):
            url = model.data(model.index(i, 0))
            rank = model.data(model.index(i, 1))
            data.append({
                "URL": url,
                "Rank": rank,
            })
        if "csv" in fileType:
            with open(filePath + ".csv", 'w') as f:
                w = csv.DictWriter(f, ["URL", "Rank"])
                w.writeheader()
                w.writerows(data)
        else:
            with open(filePath + ".json", 'w') as f:
                f.write(json.dumps(data))
