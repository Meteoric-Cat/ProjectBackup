from cv2 import PCACompute, PCAProject, PCABackProject
import numpy as np

import sys

# run when updating the system
# def add_paths():
# 	sys.path.insert(0, './temp')
# add_paths()


import file_system_manager as fm
import utils as ut
import database_manager as db
import db_utils as dbut

def find_meanface_and_eigenfaces(component_count = 30):
	'''get matrix of images, calculate mean, eigenvectors and save them in file'''
	images, filePaths = fm.read_facial_images_into_matrix()
	
	meanface, eigenfaces = PCACompute(images, np.empty((0)), maxComponents = component_count)
	checkOld = fm.write_meanface_and_eigenfaces(meanface, eigenfaces)

	#perform projection and save data to the database
	projectionResult = PCAProject(images, meanface, eigenfaces)
	db.create_subspace_images(filePaths, projectionResult, remove = checkOld)

	return meanface, eigenfaces

def detect_face(image, mean, eigenfaces, dist_threshold = 1500):
	if (mean is None):
		mean, eigenfaces = fm.read_meanface_and_eigenfaces(None)

	temp = image.flatten()
	tempImage = np.zeros((1, temp.shape[0]))
	tempImage[0, :] = temp[:]
	# print(type(tempImage[0, 0]), type(mean[0, 0]))	

	projectionResult = PCAProject(tempImage, mean, eigenfaces)	
	reconstructedImage = PCABackProject(projectionResult, mean, eigenfaces)
	# print("DETECTION DIST:", ut.euclid_dist(reconstructedImage, tempImage))
	
	dist = ut.euclid_dist(reconstructedImage, tempImage)
	if (dist < dist_threshold):
		return True, dist
	return False, dist

def recognize_face(image, mean = None, eigenfaces = None, 
		index_list = None, subspace_images = None, subspace_image_weights = None, dist_threshold = 5):
	if (mean is None):
		mean, eigenfaces = fm.read_meanface_and_eigenfaces(None)

	temp = image.flatten()
	tempImage = np.zeros((1, temp.shape[0]))
	tempImage[0, :] = temp[:]
	projectionResult = PCAProject(tempImage, mean, eigenfaces)

	if (subspace_images is None):
		subspace_images = db.get_subspace_images()
		subspace_image_weights = dbut.aggregate_subspaceimage_weights(subspace_images)
		index_list = range(0, len(subspace_images))

	min_dist = 1000000000
	personId = -1
	#print(index_list)
	for index in index_list:
		dist = ut.euclid_dist(subspace_image_weights[index], projectionResult)		
		# print("RECOGNITION DIST", dist)
		if (dist < min_dist):
			min_dist = dist
			personId = subspace_images[index].OwnerId

	if (min_dist > dist_threshold):
		personId = -1
	# print('recognize dist', min_dist)
	return personId, min_dist

def find_meanface_and_eigenfaces2():
	images, filePaths = fm.read_facial_images_into_matrix(as_row = False)
	#meanface, eigenfaces = PCACompute(images)

if (__name__ == '__main__'):
	find_meanface_and_eigenfaces()
	db.clean_up()









