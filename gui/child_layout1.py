from PySide2 import QtCore as qtcore 
from PySide2 import QtWidgets as qtw 

from gc import collect

import region_locator as fl
from constants import BUTTON_H, BUTTON_W, CHILD1_TO_CHILD2, CHILD1_TO_CHILD3

class ChildLayout1(qtw.QWidget):

	def __init__(self, parent):
		super().__init__()
		self.parent = parent

		self.create_views()
		self.connect_handlers()

	def create_views(self):
		self.layout = qtw.QVBoxLayout()
		self.setLayout(self.layout)

		self.create_recognization_button()
		self.create_update_button()
		self.create_usermanagement_button()

	def create_recognization_button(self):
		self.recognizationButton = qtw.QPushButton("Recognize faces")
		self.recognizationButton.setMinimumSize(BUTTON_W, BUTTON_H)
		self.recognizationButton.setMaximumSize(BUTTON_W, BUTTON_H)
		self.layout.addWidget(self.recognizationButton)
		
	def create_update_button(self):
		self.updateButton = qtw.QPushButton("Update Re-system")
		self.updateButton.setMaximumSize(BUTTON_W, BUTTON_H)
		self.updateButton.setMinimumSize(BUTTON_W, BUTTON_H)
		self.layout.addWidget(self.updateButton)

	def create_usermanagement_button(self):
		self.managementButton = qtw.QPushButton("Manage Information")
		self.managementButton.setMinimumSize(BUTTON_W, BUTTON_H)
		self.managementButton.setMaximumSize(BUTTON_W, BUTTON_H)
		self.layout.addWidget(self.managementButton)

	def connect_handlers(self):
		self.recognizationButton.clicked.connect(self.handle_recognization_button)				
		self.updateButton.clicked.connect(self.handle_update_button)
		self.managementButton.clicked.connect(self.handle_management_button)

	@qtcore.Slot()
	def handle_recognization_button(self):
		fileName = qtw.QFileDialog.getOpenFileName(None, self.tr("Choose Image"), "./input")[0]
		#self.parent.display_image(fileName)

		fileName = fl.detect_and_recognize_faces(fileName, self.parent.dataReference)
		self.parent.display_image(fileName)

		collect()

	@qtcore.Slot()
	def handle_update_button(self):
		self.parent.switch_child_layout(CHILD1_TO_CHILD2)	
		self.parent.handle_system_updating()

		collect()


	def handle_management_button(self):
		self.parent.switch_child_layout(CHILD1_TO_CHILD3)

		collect()