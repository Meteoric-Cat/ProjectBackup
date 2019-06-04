import cv2

import utils as ut 
import numpy as np

from math import acos, pi, sqrt

def build_binary_skin_map(image, m, n, tempX, tempY):
	result = np.zeros((m, n))

	for i in tempX:
		for j in tempY:
			y = 16 + 65.481 * image[i, j, 0] + 128.553 * image[i, j, 1] + 24.966 * image[i, j, 2]
			cg = 128 + (-81.085 * image[i, j, 0]) + 112 * image[i, j, 1] + (-30.915 * image[i, j, 2])
			cr = 128 + 112 * image[i, j, 0] + (-93.786 * image[i, j, 1]) + (-18.214 * image[i, j, 2])

			temp = sqrt((image[i, j, 0] - image[i, j, 1])**2 + 
				(image[i, j, 0] - image[i, j, 2]) * (image[i, j, 1] - image[i, j, 2]))
			if (temp == 0):
				temp = 1
			h = acos(0.5 * (2 * image[i, j, 0] - image[i, j, 1] - image[i, j, 2]) / temp) 

			temp = image[i, j, 0] + image[i, j, 1] + image[i, j, 2]
			if (temp == 0):
				temp = 3
			s = 1 - 3 * min(image[i, j, 0], image[i, j, 1], image[i, j, 2]) / temp
			v = (1 / 3) * temp

			if (y > 80):
				if (100 < cg < 130):
					if (135 < cr < 175):
						#if (0.05 < h < 0.9412):
						result[i, j] = 1
	return result	


def get_useful_regions_base_on_ratio(image, region_list, 
		area_size = (30, 30), aspect_ratio = (0.8, 2.6), occupancy_ratio = 0.4):
	temp = range(1, len(region_list))
	result = []
	width = height = 0
	
	for i in temp:
		region = region_list[i]
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

	for i in tempX:
		for j in tempY:
			if (steps[i, j] == 0):
				if (image[i, j] == 0):
					regionInfo = [i, j, i, j, 0]					
					ut.scan_region(image, steps, m, n, i, j, 1, regionInfo, temp)

					height = abs(regionInfo[0] - regionInfo[2])
					width = abs(regionInfo[1] - regionInfo[3])
					if (width * height == 0):
						continue

					if (aspect_ratio[0] <= (height / width) <= aspect_ratio[1]):
						if (occupancy_ratio <= (regionInfo[4] / (width * height))):
							if (width_ratio[0] <= (width / n) <= width_ratio[1]):
								possible_eye_info.append(regionInfo)

def match_eyes(image, m, n, possible_eye_info, pair_size_error = 5, dist_ratio = (0.2, 0.65)):
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
	ut.transform_with_open_operator(region_skin_image, eyeBlockInfo, m, n, tempX, tempY)	
	
	eyeBlockInfo = []
	find_possible_eye_blocks(region_skin_image, m, n, tempX, tempY, eyeBlockInfo, width_ratio = (0.02, 0.4))	
	#print(eyeBlockInfo)
	eyeBlockInfo = match_eyes(region_skin_image, m, n, eyeBlockInfo, dist_ratio = (0, 0.65))

	print(eyeBlockInfo)
	return eyeBlockInfo

def find_longest_border(region_skin_image, m, n, tempX, tempY):
	'''the longest border is also the border of the face in this region'''
	result = []
	steps = np.zeros[(m, n)]
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
	
	farthestPoint = ut.find_the_farthest_point(line, border)
	specialVector = [farthestPoint[0] - point[0], farthestPoint[1] - point[1]]

	perpendicularVector = [eye1[1] - eye2[1], eye2[0] - eye1[0]]
	if (ut.find_angle_between_two_vectors(perpendicularVector, specialVector) < 90):
		return perpendicularVector
	return [eye2[1] - eye1[1], eye1[0] - eye2[0]]

def transform_base_on_eye_pairs(region_image, region_skin_image, eye_pairs,
		m, n, tempX, tempY, directory):
	faceBorder = find_longest_border(region_skin_image, m, n, tempX, tempY)
	downVector = [0, -1]
	count = 0

	for eye1, eye2 in eye_pairs:
		centroid1 = [(eye1[0] + eye1[2]) / 2, (eye1[1] + eye1[3]) / 2]
		centroid2 = [(eye2[0] + eye2[2]) / 2, (eye2[1] + eye2[3]) / 2]

		pivot = [(centroid1[0] + centroid2[0]) / 2, (centroid1[1] + centroid2[1]) / 2]

		direction = get_face_direction(region_skin_image, m, n, tempX, tempY, faceBorder, centroid1, centroid2, pivot)
		angleToRotate = ut.find_angle_between_two_vectors(downVector, direction)
		if (direction[0] < 0):
			angleToRotate = -angleToRotate

		tempImage = region_image.copy()
		tempSkinImage = region_skin_image.copy()

		mat = cv2.GetRotationMatrix(pivot, angleToRotate, 1.0)
		tempImage = cv2.warpAffine(tempImage, mat, tempImage.shape[1::-1])
		tempSkinImage = cv2.warpAffine(tempSkinImage, mat, tempImage.shape[1::-1])

		count += 1
		cv2.imwrite((directory + "/hello%s.jpg") % count, tempImage)
		cv2.imwrite((directory + "/skin%s.jpg") % count, tempSkinImage)

def get_possible_face_regions(image, m, n, tempX, tempY):
	if (m == -1):
		print("something wrong 0")
		return

	#ut.balance_color(image, m, n, tempX, tempY)
	image = ut.white_balance(image).astype(np.float)
	skinMap = build_binary_skin_map(image, m, n, tempX, tempY)
	# print('hello1')
	# ut.filter_with_binary_median_filter(skinMap, m, n, tempX, tempY)

	# regionInfo = [['hello world']]
	# # kernel = np.ones((3,3))
	# # skinMap = cv2.morphologyEx(skinMap, cv2.MORPH_OPEN, kernel)
	# print('hello2')
	# ut.transform_with_open_operator(skinMap, regionInfo, m, n, tempX, tempY)	

	# print('hello3')
	# regionInfo = get_useful_regions_base_on_ratio(skinMap, regionInfo, 
	# 	area_size = (40, 40), aspect_ratio = (0.2, 4.6), occupancy_ratio = 0.2)
	# print(len(regionInfo))

	# result = []	
	# for region in regionInfo:
	# 	tempImage = skinMap[region[0]:region[2], region[1]:region[3]]
	# 	m, n, tempX, tempY = ut.get_size_and_ranges(tempImage)

	# 	#tempImage values have been reversed
	# 	print('hello')
	# 	eyePairs = get_eye_pairs(tempImage, m, n, tempX, tempY)

	# 	if (len(eyePairs) > 0):
	# 		result.append(region)		
	# regionInfo = result
	# print(len(regionInfo))

	#display image to check the bounding box
	image = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_RGB2GRAY)
	image[:, :] = skinMap[:, :] * 255
	
	image = image.astype(np.uint8)
	# temp = len(regionInfo)
	# if (temp > 0):
	# 	for i in range(0, temp):
	# 		cv2.rectangle(image, (regionInfo[i][1], regionInfo[i][0]), (regionInfo[i][3],regionInfo[i][2]), (0, 255, 0), 2)
	
	cv2.imshow('friend', image)
	cv2.waitKey(0)
	cv2.destroyWindow('friend')

	#divide image and save it to database
	# ut.split_image_into_images(image.astype(np.uint8), regionInfo, directory = "face_database/development/hello%s.jpg")


def scan_useful_region(image, m, n, steps, region_info, regionCount, i, j, temp, temp1):
	# if (steps[i, j] != 0):
	# 	return

	for k in temp:
		if (image[i + ROUNDX[k], j + ROUNDY[k]] == 0):
			return 
	steps[i, j] = regionCount
	region_info[regionCount][4] += 1
	for k in temp:
		image[i + ROUNDX[k], j + ROUNDY[k]] += 1

	#if (i <= region_info[regionCount][0]):
	region_info[regionCount][0] = min(i, region_info[regionCount][0])
	region_info[regionCount][1] = min(j, region_info[regionCount][1])
	#else:
	#if (i >= region_info[regionCount][2]):
	region_info[regionCount][2] = max(i, region_info[regionCount][2])
	region_info[regionCount][3] = max(j, region_info[regionCount][3])

	# for k in temp1:
	# 	if (0 < i + STEPX[k] < m):
	# 		if (0 < j + STEPY[k] < n):				
	# 			scan_useful_region(image, m, n, steps, region_info, regionCount, i + STEPX[k], j + STEPY[k], temp, temp1)

	for k in temp1:
		valuex = i + STEPX[k]
		valuey = j + STEPY[k]

		if (0 < valuex < m):
			if (0 < valuey < n):
				if (steps[valuex, valuey] == 0):
					scan_useful_region(image, m, n, steps, region_info, regionCount, valuex, valuey, temp, temp1)

def transform_with_open_operator(image, region_info, m = None, n = None, tempX = None, tempY = None, filter_size = 3):
	if (filter_size != 3):
		print('this filter has not been supported')
		return

	if (m == None):
		m, n, tempX, tempY = get_size_and_ranges(image)
		if (m == -1):
			print('something wrong 5')
			return

	if (region_info == None):
		print('something wrong 6')
		return

	temp = range(0, 9)
	temp1 = range(0, 4)
	regionCount = 0
	steps = np.zeros((m, n))
	tempX = range(1, m - 1)
	tempY = range(1, n - 1)
	surround = True

	for i in tempX:
		for j in tempY:
			if (image[i, j] == 1):
				if (steps[i, j] == 0):
					surround = True
					for k in temp:
						if (0 <= i + ROUNDX[k] < m):
							if (0 <= j + ROUNDY[k] < n):
								if (image[i + ROUNDX[k], j + ROUNDY[k]] != 1):
									surround = False
									break
					if (surround):
						regionCount += 1
						region_info.append([i, j, i, j, 0])

						scan_useful_region(image, m - 1, n - 1, steps, region_info, regionCount, i, j, temp, temp1)

	for i in tempX:
		for j in tempY:
			if (image[i, j] <= 1):
				image[i, j] = 0
			else:
				image[i, j] = 1

def scan_region(image, steps, m, n, i, j, region_value, region_info, temp):	
	steps[i, j] = 1
	region_info[4] += 1

	region_info[0] = min(i, region_info[0])
	region_info[1] = min(j, region_info[1])

	region_info[2] = max(i, region_info[2])
	region_info[3] = max(j, region_info[3])

	for k in temp:
		valuex = i + STEPX[k]
		valuey = j + STEPY[k]

		if (0 <= valuex < m):
			if (0 <= valuey < n):
				if (steps[valuex, valuey] == 0):
					if (image[valuex, valuey] == region_value):
						scan_region(image, steps, m, n, valuex, valuey, region_value, region_info, temp)

