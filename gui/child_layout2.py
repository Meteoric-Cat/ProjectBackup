from PySide2 import QtCore as qtcore
from PySide2 import QtWidgets as qtw 
from PySide2 import QtGui as qtgui 

from constants import BUTTON_H, BUTTON_W, CHILD2_TO_CHILD1

import database_manager as db 
import file_system_manager as fm 
import system_updater as su 

import cv2

LAYER2_SIZE = (400, 600)
LAYER2_EDITOR_SIZE = (300, 50)

IMAGE_SIZE=(100, 100)
SCROLL_SIZE=(1200, 1000)
BOARD_SIZE=(1200, 2000)

class ChildLayout2(qtw.QWidget):
	def __init__(self, parent):
		super().__init__()

		self.parent = parent
		self.facesInfo = -1
		self.doneSaving = False

		self.create_layer1()
		self.create_layer2()

	def create_layer1(self):
		self.layout1 = qtw.QVBoxLayout()
		self.setLayout(self.layout1)

		self.layer2 = qtw.QWidget()
		self.layout2 = qtw.QGridLayout()
		self.layer2.setMinimumSize(LAYER2_SIZE[0], LAYER2_SIZE[1])
		self.layer2.setMaximumSize(LAYER2_SIZE[0], LAYER2_SIZE[1])	
		self.layer2.setLayout(self.layout2)
		self.layout1.addWidget(self.layer2)

		self.create_buttons()
		self.create_distlabels()

	def create_buttons(self):
		self.saveButton = qtw.QPushButton("Save")
		self.saveButton.setMaximumSize(BUTTON_W, BUTTON_H)
		self.saveButton.setMinimumSize(BUTTON_W, BUTTON_H)
		self.layout1.addWidget(self.saveButton)
		self.layout1.setAlignment(self.saveButton, qtcore.Qt.AlignHCenter | qtcore.Qt.AlignVCenter)
		# self.layout1.setAlignment(self.saveButton, qtcore.Qt.AlignTop)

		self.cancelButton = qtw.QPushButton("Cancel")
		self.cancelButton.setMinimumSize(BUTTON_W, BUTTON_H)
		self.cancelButton.setMaximumSize(BUTTON_W, BUTTON_H)
		self.layout1.addWidget(self.cancelButton)
		self.layout1.setAlignment(self.cancelButton, qtcore.Qt.AlignHCenter | qtcore.Qt.AlignVCenter)
		# self.layout1.setAlignment(self.cancelButton, qtcore.Qt.AlignTop)

		self.saveButton.clicked.connect(self.handle_saving)
		self.cancelButton.clicked.connect(self.handle_canceling)

	def create_distlabels(self):
		self.detectionDistLabel = qtw.QLabel()
		self.detectionDistLabel.setText("Detection dist")
		self.layout1.addWidget(self.detectionDistLabel)
		self.layout1.setAlignment(self.detectionDistLabel, qtcore.Qt.AlignHCenter | qtcore.Qt.AlignVCenter)
		# self.layout1.setAlignment(self.detectionDistLabel, qtcore.Qt.AlignTop)

		self.recognizationDistLabel = qtw.QLabel()
		self.recognizationDistLabel.setText("Recognization dist")
		self.layout1.addWidget(self.recognizationDistLabel)
		self.layout1.setAlignment(self.recognizationDistLabel, qtcore.Qt.AlignHCenter | qtcore.Qt.AlignVCenter)
		# self.layout1.setAlignment(self.recognizationDistLabel, qtcore.Qt.AlignTop)

	def create_layer2(self):
		self.create_infolabels()
		self.create_infoeditors()

	def create_infolabels(self):
		labels = ["Person ID", "Name", "Age", "Occupation"]
		self.infoLabels = []

		for i in range(0, 4):
			self.infoLabel = qtw.QLabel()
			self.infoLabel.setText(labels[i])
			self.infoLabels.append(self.infoLabel)

			self.layout2.addWidget(self.infoLabel, i, 0, 1, 1)

	def create_infoeditors(self):
		self.infoEditors = []

		for i in range(0, 4):
			self.infoEditor = qtw.QLineEdit()
			self.setMinimumSize(LAYER2_EDITOR_SIZE[0], LAYER2_EDITOR_SIZE[1])
			self.infoEditors.append(self.infoEditor)

			self.layout2.addWidget(self.infoEditor, i, 1, 1, 3)

		self.infoEditors[0].returnPressed.connect(self.handle_editor_return_event)

	def get_editors_data(self, start, end):
		result = []
		for i in range(start, end + 1):
			result.append(self.infoEditors[i].text())
		return result

	@qtcore.Slot()
	def handle_saving(self):
		if (self.infoEditors[0].text() == "" or self.imageId == -1):
			print("nothing to do")
			return

		if (self.facesInfo[self.imageId][0] <= -1):
			db.create_people(self.get_editors_data(1, 3))
			self.facesInfo[self.imageId][0] = db.get_max_personid()
			print(self.facesInfo[self.imageId][0])
		else:
			db.update_people(self.get_editors_data(0, 3))

		fm.write_facial_image_to_file(self.facesInfo[self.imageId][0], self.facesInfo[self.imageId][1])
		self.doneSaving = True

	qtcore.Slot()
	def handle_canceling(self):
		if (self.doneSaving):
			self.doneSaving = False
			su.update(self.parent.dataReference)

		self.parent.switch_child_layout(CHILD2_TO_CHILD1)

	def handle_editor_return_event(self):
		self.display_owner_data(int(self.infoEditors[0].text()))
		self.facesInfo[self.imageId][0] = int(self.infoEditors[0].text())

	def save_faces_info(self, faces_info):
		self.facesInfo = faces_info

	def display_data(self, imageId):
		if (self.facesInfo is None):
			print("something wrong")
			return

		self.imageId = imageId

		if (self.facesInfo[imageId][0] <= 0):
			self.clean_editors_up()
			self.infoEditors[0].setText(str(self.facesInfo[imageId][0]))
		else:			
			self.display_owner_data(self.facesInfo[imageId][0])

		self.detectionDistLabel.setText("Detection dist:" + str(self.facesInfo[imageId][2]))
		self.recognizationDistLabel.setText("Recognization dist:" + str(self.facesInfo[imageId][3]))

	def display_owner_data(self, owner_id):
		if (owner_id <= 0):
			return

		person = db.get_people(False, owner_id)[0]
		if not (person is None):
			self.infoEditors[0].setText(str(person.Id))
			self.infoEditors[1].setText(person.Name)
			self.infoEditors[2].setText(str(person.Age))
			self.infoEditors[3].setText(person.Occupation)

	def clean_editors_up(self):
		for editor in self.infoEditors:
			editor.setText("")

		self.detectionDistLabel.setText("")
		self.recognizationDistLabel.setText("")

class ImageBoard(qtw.QScrollArea):
	def __init__(self, parent):
		super().__init__()
		
		self.images = []
		self.spacer = qtw.QSpacerItem(IMAGE_SIZE[0], IMAGE_SIZE[1])
		self.parent = parent	
		self.visibleCount = 0	

		self.setMinimumSize(SCROLL_SIZE[0], SCROLL_SIZE[1])
		self.setMaximumSize(SCROLL_SIZE[0], SCROLL_SIZE[1])

		self.create_content_area()

	def create_content_area(self):
		self.content = qtw.QWidget()
		self.content.setMinimumSize(BOARD_SIZE[0], BOARD_SIZE[1])
		self.content.setMinimumSize(BOARD_SIZE[0], BOARD_SIZE[1])

		self.contentLayout = qtw.QGridLayout()
		self.contentLayout.setAlignment(qtcore.Qt.AlignTop | qtcore.Qt.AlignLeft)
		self.content.setLayout(self.contentLayout)

		self.setWidget(self.content)

	def update_images(self, images_info):
		# self.clean_images_up()

		count = 0
		for imageInfo in images_info:			
			path = fm.write_temp_image(imageInfo[1])
			# cv2.imshow("hello", imageInfo[1])
			# cv2.waitKey(0)
			# cv2.destroyWindow("hello")
			if (len(self.images) <= count):
				image = Image(self, count)
				self.images.append(image)

			self.images[count].add_image(path)
			self.contentLayout.addWidget(self.images[count], int(count / 12), count % 12, 1, 1)			
			#self.contentLayout.setAlignment(self.images[count], qtcore.Qt.AlignLeft | qtcore.Qt.AlignTop)
			self.images[count].show()
			count += 1

		self.add_spacer(count)
		self.remove_redundant_images(count)

		self.content.update()
		self.visibleCount = count

	def add_spacer(self, count):
		spacerColumn = 12 - count % 12
		if (spacerColumn != 0):
			self.spacer.changeSize(IMAGE_SIZE[0] * spacerColumn, IMAGE_SIZE[1])
			self.contentLayout.addItem(self.spacer, int(count / 12), count % 12, 1, spacerColumn)
		
	def remove_redundant_images(self, count):
		if (self.visibleCount <= count):
			return

		for i in range(count, self.visibleCount):
			self.contentLayout.removeWidget(self.images[i])
			self.images[i].hide()

class Image(qtw.QLabel):
	def __init__(self, parent, imageId):
		'''image id is the index of the image in ImageInfo list of central view'''
		super().__init__()

		# self.personId = person_id
		self.parent = parent
		self.imageId = imageId

		self.setMaximumSize(IMAGE_SIZE[0], IMAGE_SIZE[1])
		self.setMinimumSize(IMAGE_SIZE[0], IMAGE_SIZE[1])


	def add_image(self, file_name):
		self.setPixmap(qtgui.QPixmap(file_name))
		self.update()

	def mousePressEvent(self, event):
		super().mousePressEvent(event)

		self.parent.parent.childLayout2.display_data(self.imageId)
		

