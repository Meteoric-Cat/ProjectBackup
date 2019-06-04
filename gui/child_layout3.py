from PySide2 import QtCore as qtcore
from PySide2 import QtWidgets as qtw 
from PySide2 import QtGui as qtgui 

import file_system_manager as fm 
import database_manager as db 
import system_updater as su 

from constants import BUTTON_H, BUTTON_W, CHILD3_TO_CHILD1

TABLE_HEADERS = ["ID", "NAME", "AGE", "OCCUPATION"]

class PeopleTable(qtw.QTableWidget):
	def __init__(self, parent):
		super().__init__()

		self.parent = parent
		self.setHorizontalHeaderLabels(TABLE_HEADERS)
		self.cellClicked.connect(self.handle_cell_selection)

		self.setRowCount(db.get_people_count())
		self.setColumnCount(len(TABLE_HEADERS))

		# self.populate_data()

	def populate_data(self):
		people = db.get_people(allFlag = True)
		count = 0

		for person in people:
			values = [str(person.Id)]
			if (self.item(count, 0) is None):
				for i in range(0, self.columnCount()):
					item = qtw.QTableWidgetItem()
					self.setItem(count, i, item)

			self.item(count, 0).setText(str(person.Id))
			self.item(count, 1).setText(person.Name)
			self.item(count, 2).setText(str(person.Age))
			self.item(count, 3).setText(person.Occupation)

			count += 1
		# print(count)

	def get_row_data(self, row, start_col, end_col):
		result = []
		for i in range(start_col, end_col + 1):
			result.append(self.item(row, i).text())
		return result

	def add_row(self, data):
		rowCount = self.rowCount()
		self.insertRow(rowCount)
		newPersonId = db.get_max_personid()

		newItem = qtw.QTableWidgetItem()
		self.setItem(rowCount, 0, newItem)
		newItem.setText(str(newPersonId))
		for i in range(1, len(data) + 1):
			newItem = qtw.QTableWidgetItem()
			self.setItem(rowCount, i, newItem)
			newItem.setText(data[i - 1])

	def update_row(self, row, new_data):
		for i in range(0, self.columnCount()):
			self.item(row, i).setText(new_data[i])

	@qtcore.Slot(int)
	def handle_cell_selection(self, row, column):
		self.parent.show_updating_dialog(row, self.get_row_data(row, 0, 3))

class ChildLayout3(qtw.QWidget):
	def __init__(self, parent):
		super().__init__()

		self.parent = parent
		self.layout = qtw.QVBoxLayout()
		self.setLayout(self.layout)

		self.create_buttons()
		self.attach_handlers()

	def create_buttons(self):
		self.createButton = qtw.QPushButton("Create owner")
		self.createButton.setMinimumSize(BUTTON_W, BUTTON_H)
		self.createButton.setMaximumSize(BUTTON_W, BUTTON_H)
		self.layout.addWidget(self.createButton)

		self.imageDeletingButton = qtw.QPushButton("Delete image")
		self.imageDeletingButton.setMinimumSize(BUTTON_W, BUTTON_H)
		self.imageDeletingButton.setMaximumSize(BUTTON_W, BUTTON_H)
		self.layout.addWidget(self.imageDeletingButton)

		self.backButton = qtw.QPushButton("Back")
		self.backButton.setMinimumSize(BUTTON_W, BUTTON_H)
		self.backButton.setMaximumSize(BUTTON_W, BUTTON_H)
		self.layout.addWidget(self.backButton)

	def attach_handlers(self):
		self.createButton.clicked.connect(self.handle_create_button)
		self.imageDeletingButton.clicked.connect(self.handle_imagedeleting_button)
		self.backButton.clicked.connect(self.handle_back_button)
	
	@qtcore.Slot()
	def handle_create_button(self):
		self.parent.show_creating_dialog()

	@qtcore.Slot()
	def handle_imagedeleting_button(self):
		fileName = qtw.QFileDialog.getOpenFileName(None, "Choose Image", "./image_storage/facial_images")[0]
		db.delete_subspace_images([fileName])		
		fm.remove_image(fileName)		
		su.update(self.parent.dataReference)

	@qtcore.Slot()
	def handle_back_button(self):
		self.parent.switch_child_layout(CHILD3_TO_CHILD1)





