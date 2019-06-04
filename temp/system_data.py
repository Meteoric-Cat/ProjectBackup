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

		self.detectionThreshold = 2600
		self.recognizationThreshold = 500

	def update(self, mean, eigenfaces):
		self.mean = mean
		self.eigenfaces = eigenfaces
		self.eigenfaceCount = len(self.eigenfaces)

		self.subspaceImages = db.get_subspace_images()
		self.subspaceImageWeights = dbut.aggregate_subspaceimage_weights(self.subspaceImages)

	def change_detection_threshold(self, value = None):
		'''
		this function will increase the detection threshold when updating the system data
		'''
		self.subDetectionThreshold = self.detectionThreshold
		if (value is None):
			self.detectionThreshold = 4000
		else:
			self.detectionThreshold = value

	def recover_detection_threshold(self):
		self.detectionThreshold = self.subDetectionThreshold