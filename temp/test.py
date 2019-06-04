# import find_face_candidate as ffc 
# import utils as ut 
import cv2
from sys import setrecursionlimit
import database_manager as db 
import file_system_manager as fm 
import db_utils as dbut

import pca_manager as pca

if (__name__ == "__main__"):
	setrecursionlimit(10000)

	db.renew_subspaceimages_table()
	mean, eigenfaces = pca.find_meanface_and_eigenfaces()
	print(type(eigenfaces))
	print(mean.shape)
	print(type(mean))
	subspaceImages = db.get_subspace_images()
	subspaceWeights = dbut.aggregate_subspaceimage_weights(subspaceImages)
	temp = range(0, len(subspaceImages))

	for i in range(0, 16):
		image = fm.read_test_image(name = "%s.jpg" % i)
		result = pca.detect_face(image, mean, eigenfaces, dist_threshold = 1500)		
		if (result):
			personID = pca.recognize_face(image, mean, eigenfaces, temp, subspaceImages, subspaceWeights, dist_threshold = 500)		
			print(personID)
	
	db.clean_up()

















































	# old test for database module
	# temp = input("Input id:")
	# image1 = cv2.imread("./face_database/hello%s.jpg" % temp)
	# image2 = cv2.imread("./face_database/gray%s.jpg" % temp)

	# image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
	# m, n, tempX, tempY = ut.get_size_and_ranges(image2)
	
	# eyeBlockInfo = []

	# ffc.find_possible_eye_blocks(image2, m, n, tempX, tempY, eyeBlockInfo, 
	# 	aspect_ratio = (0.2, 1.67), width_ratio = (0.028, 0.4), occupancy_ratio = 0.3)

	# eyeBlockInfo = ffc.match_eyes(image2, m, n, eyeBlockInfo)
	# print(ffc.check_and_transform_region(image2))
	# print(eyeBlockInfo)

	# cv2.imshow("gray", image2)
	# cv2.waitKey(0)