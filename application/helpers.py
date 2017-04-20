# -*- coding: UTF-8 -*-
#!/usr/bin/env python

from PyQt5.QtCore import QFile, QTextStream, QIODevice

def readTextFile(filePath):
    f = QFile(filePath)
    if not f.open(QIODevice.ReadOnly):
        return False
    ts = QTextStream(f)

    return ts.readAll()

def writeTextFile(filePath, fileContents):
    pass