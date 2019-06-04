from PySide2 import QtCore as qtcore 
from PySide2 import QtWidgets as qtw 
from PySide2 import QtGui as qtgui 

import database_manager as db 
import file_system_manager as fm
import system_updater as su

DIALOG_BUTTON_SIZE = (60, 30)
DIALOG_SIZE = (300, 400)

CREATING_DIALOG = 1
UPDATING_DIALOG = 2 

class PersonDialog(qtw.QDialog):
	def __init__(self, parent = None, mode = CREATING_DIALOG):
		'''Mode 1: creating
		   Mode 2: updating'''

		super().__init__()

		self.parent = parent
		self.mode = mode
		self.layout = qtw.QFormLayout()
		self.setLayout(self.layout)
		self.row = None

		self.setMinimumSize(DIALOG_SIZE[0], DIALOG_SIZE[1])
		self.setMaximumSize(DIALOG_SIZE[0], DIALOG_SIZE[1])

		self.create_editors()
		self.create_buttons()

		self.attach_handlers()

	def create_editors(self):
		LABELS = ["Person ID", "Name", "Age", "Occupation"]
		self.infoEditors = []
		for label in LABELS:
			infoEditor = qtw.QLineEdit()
			self.layout.addRow(label, infoEditor)
			self.infoEditors.append(infoEditor)

	def create_buttons(self):
		self.childLayout = qtw.QHBoxLayout()

		self.yesButton = qtw.QPushButton("Save")
		self.yesButton.setMinimumSize(DIALOG_BUTTON_SIZE[0], DIALOG_BUTTON_SIZE[1])
		self.yesButton.setMaximumSize(DIALOG_BUTTON_SIZE[0], DIALOG_BUTTON_SIZE[1])

		self.noButton = qtw.QPushButton("Cancel")
		self.noButton.setMinimumSize(DIALOG_BUTTON_SIZE[0], DIALOG_BUTTON_SIZE[1])
		self.noButton.setMaximumSize(DIALOG_BUTTON_SIZE[0], DIALOG_BUTTON_SIZE[1])

		self.deleteButton = qtw.QPushButton("Delete")
		self.deleteButton.setMinimumSize(DIALOG_BUTTON_SIZE[0], DIALOG_BUTTON_SIZE[1])
		self.deleteButton.setMaximumSize(DIALOG_BUTTON_SIZE[0], DIALOG_BUTTON_SIZE[1])
		
		self.childLayout.addWidget(self.yesButton)
		self.childLayout.addWidget(self.noButton)
		self.childLayout.addWidget(self.deleteButton)

		self.layout.addRow(self.childLayout)


	def attach_handlers(self):
		self.yesButton.clicked.connect(self.handle_yes_button)
		self.noButton.clicked.connect(self.handle_no_button)
		self.deleteButton.clicked.connect(self.handle_delete_button)

	def get_person_info(self, start, end):
		result = []
		for i in range(start, end + 1):
			result.append(self.infoEditors[i].text())
		return result

	def populate_data(self, row, person_data):		
		self.row = row
		count = 0
		for data in person_data:
			self.infoEditors[count].setText(data)
			count += 1

	def clean_editors_up(self):
		for editor in self.infoEditors:
			editor.setText("")

	@qtcore.Slot()
	def handle_yes_button(self):
		if (self.mode == CREATING_DIALOG):
			data = self.get_person_info(1, 3)
			db.create_people(data)			
			fm.create_person_directory(int(self.infoEditors[0].text()))
			self.parent.peopleTable.add_row(data)
		else:
			data = self.get_person_info(0, 3)
			db.update_people(data)
			self.parent.peopleTable.update_row(self.row, data)
		self.clean_editors_up()
		self.hide()

	@qtcore.Slot()
	def handle_no_button(self):
		self.clean_editors_up()
		self.hide()

	@qtcore.Slot()
	def handle_delete_button(self):
		if (self.mode == UPDATING_DIALOG):
			db.delete_people(self.get_person_info(0, 3))
			self.parent.peopleTable.removeRow(self.row)
			fm.remove_person_directory(int(self.infoEditors[0].text()))
			su.update(self.parent.dataReference)