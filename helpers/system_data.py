import file_system_manager as fm 
import database_manager as db
import db_utils as dbut

from constants import MAX_EIGENFACE_COUNT

class RunningSystemData():
	def __init__(self):
		self.mean, self.eigenfaces = fm.read_meanface_and_eigenfaces(eigenface_count = MAX_EIGENFACE_COUNT)
		self.eigenfaceCount = len(self.eigenfaces) #get the available count
		print(self.eigenfaceCount)

		self.subspaceImages = db.get_subspace_images()
		self.subspaceImageWeights = dbut.aggregate_subspaceimage_weights(self.subspaceImages)

		self.detectionThreshold = 4000
		self.recognizationThreshold = 3500

	def update(self, mean, eigenfaces):
		self.mean = mean
		self.eigenfaces = eigenfaces
		self.eigenfaceCount = len(self.eigenfaces)

		self.subspaceImages = db.get_subspace_images()
		self.subspaceImageWeights = dbut.aggregate_subspaceimage_weights(self.subspaceImages)

	def change_detection_threshold(self, new_detection_threshold = None, new_recognition_threshold = None):
		'''
		this function will increase the detection threshold when updating the system data
		'''
		self.subDetectionThreshold = self.detectionThreshold
		self.subRecognitionThreshold = self.recognizationThreshold

		if (new_detection_threshold is None):
			self.detectionThreshold = 5000
			self.recognizationThreshold = 4000
		else:
			self.detectionThreshold = new_detection_threshold
			self.recognizationThreshold = new_recognition_threshold

	def recover_detection_threshold(self):
		self.detectionThreshold = self.subDetectionThreshold
		self.recognizationThreshold = self.subRecognitionThreshold