from math import acos, pi, sqrt

import cv2
import numpy as np

import utils as ut 
import file_system_manager as fm
import database_manager as db 
import eigenface_implementer as pca


OUTPUT_SIZE = (100, 100)
#(-0.4, 1.5, 0.9, 0.9)
CLIPPING_RATIO = (-1.2, 1.8, -1.2, 1.2)
MIN_AREA_SIZE = (40, 40)
ASPECT_RATIO = (0.2, 3.6)
OCCUPANCY_RATIO = 0.3


def build_binary_skin_map2(image, m, n, tempX, tempY):
	result = np.zeros((m, n))

	for i in tempX:
		for j in tempY:
			temp = (image[i, j, 0] + image[i, j, 1] + image[i, j, 2])
			if (temp == 0):
				image[i, j, 0] = image[i, j, 1] = image[i, j, 2] = 1
				temp = 3
			r = image[i, j, 0] / temp
			g = image[i, j, 1] / temp

			temp = sqrt((image[i, j, 0] - image[i, j, 1])**2 + \
					(image[i, j, 0] - image[i, j, 2]) * (image[i, j, 1] - image[i, j, 2]))
			if (temp == 0.000000000):
				temp = 1		
			h = acos(0.5 * (2 * image[i, j, 0] - image[i, j, 1] - image[i, j, 2]) / temp) * 180 / pi
			if (image[i, j, 2] > image[i, j, 1]):
				h = 360 - h

			tempMax = max(image[i, j, 0], image[i, j, 1], image[i, j, 2])
			tempMin = min(image[i, j, 0], image[i, j, 1], image[i, j, 2])

			s = (tempMax - tempMin) / tempMax
			v = tempMax / 255

			if ((image[i, j, 0] > image[i, j, 1]) and (abs(image[i, j, 0] - image[i, j, 1]) >= 11)):
				if ((0.33 <= r <= 0.6) and (0.25 <= g <= 0.37)):
					if ((340 <= h <= 359) or (0 <= h <= 50)):
						if (0.12 <= s <= 0.7):						
							if (0.3 <= v <= 1.0):
								result[i, j] = 1

	return result	

def get_useful_regions_base_on_ratio(image, region_list, 
		area_size = (30, 30), aspect_ratio = (0.8, 2.6), occupancy_ratio = 0.4):
	result = []
	width = height = 0
	
	for region in region_list:
		#print(region)
		width = region[3] - region[1]
		height = region[2] - region[0]

		if (width * height == 0):
			continue
		if (width > area_size[0]) and (height > area_size[1]):
			if (aspect_ratio[0] <= height / width <= aspect_ratio[1]):
				if ((region[4] / (width * height)) >= occupancy_ratio):
					result.append(region)
	return result

def find_possible_eye_blocks(image, m, n, tempX, tempY, possible_eye_info, 
		aspect_ratio = (0.2, 1.67), width_ratio = (0.028, 0.4), occupancy_ratio = 0.3):
	steps = np.zeros((m, n))	
	temp = range(0, 4)

	result = []

	for regionInfo in possible_eye_info:
		height = abs(regionInfo[0] - regionInfo[2])
		width = abs(regionInfo[1] - regionInfo[3])
		if (width * height == 0):
			continue

		if (aspect_ratio[0] <= (height / width) <= aspect_ratio[1]):
			if (occupancy_ratio <= (regionInfo[4] / (width * height))):
				if (width_ratio[0] <= (width / n) <= width_ratio[1]):
					result.append(regionInfo)

	return result

def match_eyes(image, m, n, possible_eye_info, pair_size_error = 10, dist_ratio = (0.2, 0.65)):
	infoLength = len(possible_eye_info)
	temp = range(0, infoLength)
	result = []

	for i in temp:
		height1 = possible_eye_info[i][2] - possible_eye_info[i][0]
		width1 = possible_eye_info[i][3] - possible_eye_info[i][1]
		centroid1y = (possible_eye_info[i][1] + possible_eye_info[i][3]) / 2

		temp1 = range(i + 1, infoLength)

		for j in temp1:
			height2 = possible_eye_info[j][2] - possible_eye_info[j][0]
			width2 = possible_eye_info[j][3] - possible_eye_info[j][1]

			if (abs(width1 - width2) <= pair_size_error):
				if (abs(height2 - height1) <= pair_size_error):
					centroid2y = (possible_eye_info[j][1] + possible_eye_info[j][3]) / 2
					dist = abs(centroid2y - centroid1y)

					if (dist_ratio[0] <= (dist / n) <= dist_ratio[1]):
						result.append([possible_eye_info[i], possible_eye_info[j]])
						#return result				
	return result

def get_eye_pairs(region_skin_image, m, n, tempX, tempY):
	eyeBlockInfo = [["hello"]]	

	ut.reverse_binary_image(region_skin_image, m, n, tempX, tempY)	
	kernel = np.ones((2, 2))
	region_skin_image = cv2.morphologyEx(region_skin_image, cv2.MORPH_OPEN, kernel)	
	
	eyeBlockInfo = []
	ut.get_connected_regions(region_skin_image, m, n, tempX, tempY, eyeBlockInfo, 1)
	eyeBlockInfo = find_possible_eye_blocks(region_skin_image, m, n, tempX, tempY, eyeBlockInfo, width_ratio = (0, 0.4))	
	eyeBlockInfo = match_eyes(region_skin_image, m, n, eyeBlockInfo, dist_ratio = (0, 0.65))

	#print(eyeBlockInfo)
	return eyeBlockInfo

def find_longest_border(region_skin_image, m, n, tempX, tempY):
	'''the longest border is also the border of the face in this region
	each point in the border is save with the form of [row, col]'''
	result = []
	steps = np.zeros((m, n))
	temp1 = range(0, 4)
	temp2 = range(0, 9)

	for i in tempX:
		for j in tempY:
			if (ut.check_binary_border(region_skin_image, m, n, i, j, temp1)):
				if (region_skin_image[i, j] == 0):
					if (steps[i, j] == 0):
						border = []
						ut.find_binary_border(region_skin_image, steps, m, n, i, j, border, 0, temp2, temp1)
						if (len(border) > len(result)):
							result = border 
	return result

def get_face_direction(region_skin_image, m, n, tempX, tempY, border, eye1, eye2, pivot):
	'''based on nose and mouth'''
	line = ut.find_line(eye1, eye2)
	
	farthestPoint = ut.find_the_farthest_point(line, border, mode = 2)
	#border point is saved in the form of [row, col] when pivot is in the form of [col, row]
	specialVector = [farthestPoint[1] - pivot[0], farthestPoint[0] - pivot[1]]

	perpendicularVector = [eye1[1] - eye2[1], eye2[0] - eye1[0]]
	if (ut.find_angle_between_two_vectors(perpendicularVector, specialVector) < 90):
		return perpendicularVector
	return [eye2[1] - eye1[1], eye1[0] - eye2[0]]

def split_to_get_face(image, pivot, dist, ratio = CLIPPING_RATIO, output_size = OUTPUT_SIZE): 
	if len(image.shape) == 2:
		m, n = image.shape
	else:
		m, n, p = image.shape

	top = int(max(0, (pivot[1] + ratio[0] * dist)))
	bottom = int(min(m - 1, (pivot[1] + ratio[1] * dist)))
	left = int(max(0, (pivot[0] + ratio[2] * dist)))
	right = int(min(n - 1, (pivot[0] + ratio[3] * dist)))
	
	if (abs(top - bottom) < 80 or abs(left - right) < 80):
		return None

	tempImage = image[top:bottom, left:right]
	tempImage = cv2.resize(tempImage, output_size)

	return tempImage

def get_faces_base_on_eye_pairs(system_data, image, region_info, region_skin_image, eye_pairs,
		m, n, tempX, tempY):
	faceBorder = find_longest_border(region_skin_image, m, n, tempX, tempY)
	downVector = [0, 1]
	# count = 0
	# minDist = 100000000
	# minImage = None

	result = []

	for eye1, eye2 in eye_pairs:
		centroid1 = [(eye1[1] + eye1[3]) / 2, (eye1[0] + eye1[2]) / 2]
		centroid2 = [(eye2[1] + eye2[3]) / 2, (eye2[0] + eye2[2]) / 2]
		pivot = [(centroid1[0] + centroid2[0]) / 2, (centroid1[1] + centroid2[1]) / 2]

		direction = get_face_direction(region_skin_image, m, n, tempX, tempY, faceBorder, centroid1, centroid2, pivot)		
		angleToRotate = ut.find_angle_between_two_vectors(downVector, direction)
		# print(count + 1, angleToRotate) 
		# print(direction)
		if (direction[0] > 0):
			angleToRotate = -angleToRotate

		#adjust pivot point to work with original image
		pivot[0] = pivot[0] + region_info[1]
		pivot[1] = pivot[1] + region_info[0]
		pivot = tuple(pivot)

		tempImage = image.copy()
		# cv2.rectangle(tempImage, (eye1[1], eye1[0]), (eye1[3], eye1[2]), (0, 255, 0), 1)
		# cv2.rectangle(tempImage, (eye2[1], eye2[0]), (eye2[3], eye2[2]), (0, 255, 0), 1)
		mat = cv2.getRotationMatrix2D(pivot, angleToRotate, 1.0)
		tempImage = cv2.warpAffine(tempImage, mat, tempImage.shape[1::-1])

		tempImage = split_to_get_face(tempImage, pivot, ut.distance_between_points(centroid1, centroid2))
		if (tempImage is None):
			continue			
		check, dist = pca.detect_face(tempImage, system_data.mean, system_data.eigenfaces, 
			dist_threshold = system_data.detectionThreshold)

		print("DETECTION DIST", dist)
		# cv2.imshow("value", tempImage)
		# cv2.waitKey(0)
		# cv2.destroyWindow("value")

		if (check):
			# if (dist < minDist):
			# 	minDist = dist
			# 	minImage = tempImage

			result.append([dist, tempImage])

	# return minDist, minImage
	return result

def get_possible_faces(mode, system_data, image, m, n, tempX, tempY):
	'''
	 mode 1: for detection only
	 mode 2: for recognization
	'''
	# ut.balance_color(image, m, n, tempX, tempY)
	# image = ut.white_balance(image)
	# image = ut.white_balance(image)
	# image = ut.white_balance(image)
	# image = ut.white_balance(image)
	# image = ut.white_balance(image)
	# image = ut.white_balance(image)
	# image = ut.white_balance(image)
	image = image.astype(np.float)

	print('hello3')
	skinMap = build_binary_skin_map2(image, m, n, tempX, tempY)

	print('hello4')
	ut.filter_with_binary_median_filter(skinMap, m, n, tempX, tempY)

	regionInfo = []
	kernel = np.ones((3,3))
	skinMap = cv2.morphologyEx(skinMap, cv2.MORPH_OPEN, kernel)
	print('hello5')
	ut.get_connected_regions(skinMap, m, n, tempX, tempY, regionInfo, 1)

	print('hello6')
	regionInfo = get_useful_regions_base_on_ratio(skinMap, regionInfo, 
		area_size = MIN_AREA_SIZE, aspect_ratio = ASPECT_RATIO, occupancy_ratio = OCCUPANCY_RATIO)

	print('hello7')
	result = []	
	image = image.astype(np.uint8)
	grayscaleImage = cv2.cvtColor(image.copy(), cv2.COLOR_RGB2GRAY)
	indexList = range(0, len(system_data.subspaceImages))

	for region in regionInfo:
		tempSkinImage = skinMap[region[0]:region[2], region[1]:region[3]].copy()

		tempM, tempN, tempTempX, tempTempY = ut.get_size_and_ranges(tempSkinImage)

		#tempImage values have been reversed
		eyePairs = get_eye_pairs(tempSkinImage, tempM, tempN, tempTempX, tempTempY)		

		if (len(eyePairs) > 0):
			# detectionDist, regionImage = get_faces_base_on_eye_pairs(system_data, grayscaleImage, region, tempSkinImage, 
			# 	eyePairs, tempM, tempN, tempTempX, tempTempY)

			regionImages = get_faces_base_on_eye_pairs(system_data, grayscaleImage, region, tempSkinImage, 
				eyePairs, tempM, tempN, tempTempX, tempTempY)

			minRecognizationDist = 100000
			minImage = None
			personId = -1

			for regionImage in regionImages:
				tempId, recognizationDist = pca.recognize_face(regionImage[1], system_data.mean, system_data.eigenfaces, indexList,
				system_data.subspaceImages, system_data.subspaceImageWeights, 
				dist_threshold = system_data.recognizationThreshold)

				if (mode != 1):
					if (recognizationDist < minRecognizationDist):
						minRecognizationDist = recognizationDist
						minImage = regionImage
						personId = tempId
				else:
					result.append([tempId, regionImage[1], regionImage[0], recognizationDist])

			if (mode != 1):
				if not (minImage is None):
					result.append([personId, region, minImage[0], minRecognizationDist])
	
	return result		

	#display image to check the bounding box
	# image = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_RGB2GRAY)
	# image[:, :] = skinMap[:, :] * 255
	
	# image = image.astype(np.uint8)
	# temp = len(regionInfo)
	# if (temp > 0):
	# 	for i in range(0, temp):
	# 		cv2.rectangle(image, (regionInfo[i][1], regionInfo[i][0]), (regionInfo[i][3],regionInfo[i][2]), (0, 255, 0), 2)
	
	# cv2.imshow('friend', image)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()

	#divide image and save it to database
	# ut.split_image_into_images(image.astype(np.uint8), regionInfo, directory = "face_database/development/hello%s.jpg")

def detect_and_recognize_faces(file_name, system_data):
	image, m, n, tempX, tempY = fm.read_image(file_name)
	if (m == -1):
		print("something wrong 0")
		return

	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	faceInfo = get_possible_faces(2, system_data, image, m, n, tempX, tempY)
	image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

	for face in faceInfo:
		region = face[1]
		cv2.rectangle(image, (region[1], region[0]), (region[3], region[2]), 
			(0, 255, 0), 2)
		if (face[0] == -1):
			face[0] = "unknown"
		else:
			person = db.get_people(False, face[0])
			face[0] = person[0].Name
		cv2.putText(image, str(face[0]), (region[1], region[0] + 15), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)

	return fm.write_temp_image(image)

def detect_faces_to_update_system(file_name, system_data, new_threshold = None):
	image, m, n, tempX, tempY = fm.read_image(file_name)
	if (m == -1):
		print("something wrong 1")
		return
	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

	if (new_threshold is None):
		system_data.change_detection_threshold(5000, 4000)
	else:
		system_data.change_detection_threshold(new_threshold, 4000)
	faceInfo = get_possible_faces(1, system_data, image, m, n, tempX, tempY)
	system_data.recover_detection_threshold()

	return faceInfo


