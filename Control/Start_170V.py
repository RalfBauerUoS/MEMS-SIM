# -*- coding: utf-8 -*-
"""
Created on Sun Jan 8 20:50:00 2022

@author: Ralf
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication

from MEMSSIM_MainWindow import MainWindow

app = QApplication([])
start_window = MainWindow()
start_window.show()
app.exit(app.exec_())