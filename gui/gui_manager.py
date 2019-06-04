import sys
from PySide2 import QtCore as qtcore 
from PySide2 import QtWidgets as qtw

import central_view
import system_data
import database_manager as db 

from constants import WINDOW_W, WINDOW_H

class MainWindow(qtw.QWidget):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("Hello world")
		self.layout = central_view.CentralView()
		self.setLayout(self.layout)

def run_application():
	app = qtw.QApplication()

	mainWindow = MainWindow()
	mainWindow.resize(WINDOW_W, WINDOW_H)
	mainWindow.show()

	systemData = system_data.RunningSystemData()
	mainWindow.layout.dataReference = systemData

	app.exec_()
	db.clean_up()

