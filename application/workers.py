# -*- coding: UTF-8 -*-
#!/usr/bin/env python

from time import sleep

from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal, QObject

from .utils import check_alexa

class Worker(QObject):
    start = pyqtSignal()
    stop = pyqtSignal()
    finished = pyqtSignal()
    result = pyqtSignal(object)

    def __init__(self, func, *args, **kwargs):
        super(Worker, self).__init__()
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._running = True
        self.start.connect(self.run)
        self.stop.connect(self.onStop)

    @pyqtSlot()
    def run(self):
        result = self.doWork(*self._args, **self._kwargs)
        self.finished.emit()

    @pyqtSlot()
    def onStop(self):
        self._running = False

    def doWork(self, *args, **kwargs):
        raise NotImplementedError

class CheckAlexaWorker(Worker):
    status = pyqtSignal(tuple)

    def doWork(self, *args, **kwargs):
        queue = kwargs["queue"]
        timeout = kwargs["timeout"]
        delay = kwargs["delay"]
        while self._running and not queue.empty():
            row, url = queue.get()
            self.status.emit((row, "Checking ..."))
            rank, status, msg = check_alexa(url, timeout)
            result = True if rank else False
            self.result.emit({
                "row": row,
                "url": url,
                "result": result,
                "rank": rank,
                "status": status,
            })
            self.status.emit((row, "Done"))
            sleep(delay)