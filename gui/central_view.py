import sys
from PySide2 import QtCore as qtcore
from PySide2 import QtWidgets as qtw 
from PySide2 import QtGui as qtgui 

import child_layout1 as cl1 
import child_layout2 as cl2
import child_layout3 as cl3 

from constants import CHILD_LAYOUT_W, CHILD_LAYOUT_H, IMAGE_W, IMAGE_H
from constants import CHILD1_TO_CHILD2, CHILD2_TO_CHILD1, CHILD1_TO_CHILD3, CHILD3_TO_CHILD1

import region_locator as fl 
import file_system_manager as fm 
import input_dialog as dialogs

class CentralView(qtw.QHBoxLayout):
	def __init__(self):
		super().__init__()

		self.dataReference = None

		self.create_layout1()
		self.create_layout2()
		self.create_layout3()
		self.create_dialogs()

	def create_layout1(self):	
		self.image = qtw.QLabel()
		self.image.setMinimumSize(IMAGE_W, IMAGE_H)
		self.image.setMaximumSize(IMAGE_W, IMAGE_H)		
		self.addWidget(self.image)
		self.image.setAlignment(qtcore.Qt.AlignHCenter | qtcore.Qt.AlignVCenter)
		self.image.show()

		self.childLayout1 = cl1.ChildLayout1(self)
		self.childLayout1.setMinimumSize(CHILD_LAYOUT_W, CHILD_LAYOUT_H)
		self.childLayout1.setMaximumSize(CHILD_LAYOUT_W, CHILD_LAYOUT_H)		
		self.addWidget(self.childLayout1)
		self.childLayout1.show()

	def create_layout2(self):
		self.imageBoard = cl2.ImageBoard(self)
		self.imageBoard.hide()

		self.childLayout2 = cl2.ChildLayout2(self)	
		self.childLayout2.setMinimumSize(CHILD_LAYOUT_W, CHILD_LAYOUT_H)
		self.childLayout2.setMaximumSize(CHILD_LAYOUT_W, CHILD_LAYOUT_H)
		self.childLayout2.hide()

	def create_layout3(self):
		self.peopleTable = cl3.PeopleTable(self)
		self.peopleTable.setMinimumSize(IMAGE_W, IMAGE_H)
		self.peopleTable.setMaximumSize(IMAGE_W, IMAGE_H)
		self.peopleTable.hide()

		self.childLayout3 = cl3.ChildLayout3(self)
		self.childLayout3.setMinimumSize(CHILD_LAYOUT_W, CHILD_LAYOUT_H)
		self.childLayout3.setMaximumSize(CHILD_LAYOUT_W, CHILD_LAYOUT_H)
		self.childLayout3.hide()

	def create_dialogs(self):
		self.personDialog = dialogs.PersonDialog(self)
		self.personDialog.hide()

	def display_image(self, image):
		#self.pixmap.swap(qtgui.QPixmap(image))	
		self.image.setPixmap(qtgui.QPixmap(image))
		self.image.update()

	def remove_widget(self, widget):
		self.removeWidget(widget)
		widget.hide()

	def add_widget(self, widget):
		self.addWidget(widget)
		widget.show()

	def switch_child_layout(self, mode):
		if (mode == CHILD1_TO_CHILD2):			
			self.remove_widget(self.childLayout1)			
			self.remove_widget(self.image)

			self.add_widget(self.imageBoard)
			self.childLayout2.clean_editors_up()
			self.add_widget(self.childLayout2)
		
		if (mode == CHILD2_TO_CHILD1):
			self.remove_widget(self.childLayout2)
			self.remove_widget(self.imageBoard)

			self.add_widget(self.image)
			self.add_widget(self.childLayout1)			

		if (mode == CHILD1_TO_CHILD3):
			self.remove_widget(self.childLayout1)
			self.remove_widget(self.image)

			self.peopleTable.populate_data()
			self.add_widget(self.peopleTable)
			self.add_widget(self.childLayout3)

		if (mode == CHILD3_TO_CHILD1):
			self.remove_widget(self.childLayout3)
			self.remove_widget(self.peopleTable)

			self.add_widget(self.image)
			self.add_widget(self.childLayout1)
			
		self.update()

	def show_creating_dialog(self):
		self.personDialog.mode = dialogs.CREATING_DIALOG  
		self.personDialog.show()

	def show_updating_dialog(self, row, person_data):
		self.personDialog.mode = dialogs.UPDATING_DIALOG 
		self.personDialog.populate_data(row, person_data)
		self.personDialog.show()

	def handle_system_updating(self):		
		fileName = qtw.QFileDialog.getOpenFileName(None, self.tr("Choose Image"), "./input/ADDED")[0]
		facesInfo = fl.detect_faces_to_update_system(fileName, self.dataReference)

		if (facesInfo is None):
			return

		self.childLayout2.save_faces_info(facesInfo)
		self.imageBoard.update_images(facesInfo)

