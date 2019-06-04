from cv2 import imwrite, imread, IMREAD_GRAYSCALE, resize

import os
import csv
import numpy as np

import database_manager as db
import utils as ut

IMAGE_PATH = "image_storage"
OUTPUT_SIZE = (100, 100)

def read_facial_images_into_matrix(personCount = None, directory = None, as_rows = True, image_size = OUTPUT_SIZE):
	imageCount = 0
	temp = None
	imagePerPerson = []

	if (directory is None):
		directory = IMAGE_PATH + "/facial_images/person_%s"

	peopleIds = []
	if (personCount is None):
		people = db.get_people(allFlag = True)
		# temp = range(1, personCount + 1)		
		for person in people:
			imageCount += len(list(os.scandir(directory % person.Id)))
			peopleIds.append(person.Id)

	result = None
	fileInfo = []

	if (as_rows):
		result = np.zeros((imageCount, image_size[0] * image_size[1]))
		count = 0
		for tempId in peopleIds:
			entries = os.scandir(directory % tempId)
			for entry in entries:
				tempImage = imread(entry.path, IMREAD_GRAYSCALE)
				tempImage = tempImage.flatten()				

				result[count, :] = tempImage[:]
				fileInfo.append([tempId, str(entry.path)])
				count += 1
	else:
		result = np.zeros((image_size[0] * image_size[1], imageCount))
		count = 0
		for tempId in peopleIds:
			entries = os.scandir(directory % tempId)
			for entry in entries:
				tempImage = imread(entry.path, IMREAD_GRAYSCALE)
				tempImage = tempImage.flatten()

				result[:, count] = tempImage[:]
				fileInfo.append([tempId, str(entry.path)])
				count += 1

	return (result, fileInfo)

def clean_eigenface_images_up(directory = IMAGE_PATH + "/eigenface_images"):
	os.remove(directory + '/mean.jpg')
	os.remove(directory + '/eigenfaces.csv')

	# entries = os.scandir(directory)
	# for entry in entries:
	# 	os.remove(entry.path)

def write_meanface_and_eigenfaces(mean, eigenfaces, directory = None, output_size = OUTPUT_SIZE):
	check = False

	if (directory is None):
		directory = IMAGE_PATH + "/eigenface_images"		
	if (os.path.exists(directory + "/mean.jpg")):
		clean_eigenface_images_up()
		check = True

	temp = mean.reshape(output_size)
	imwrite(directory + "/mean.jpg", temp)
	
	with open(directory + "/eigenfaces.csv", "w") as csvFile:
		csvWriter = csv.writer(csvFile, delimiter = ",", quotechar = '"', quoting = csv.QUOTE_MINIMAL)

		for eigenface in eigenfaces:
			csvWriter.writerow(list(eigenface))

	return check

def read_meanface_and_eigenfaces(directory = None, eigenface_count = 11):
	if (directory is None):
		directory = IMAGE_PATH + "/eigenface_images"

	mean = imread(directory + "/mean.jpg", IMREAD_GRAYSCALE).reshape(1, OUTPUT_SIZE[0] * OUTPUT_SIZE[1]).astype(np.float)

	eigenfaces = None
	with open(directory + "/eigenfaces.csv") as csvFile:
		csvReader = csv.reader(csvFile, delimiter=",")

		rows = np.zeros((eigenface_count, OUTPUT_SIZE[0] * OUTPUT_SIZE[1]))
		rowCount = 0
		for row in csvReader:
			j = 0
			for value in row:
				rows[rowCount, j] = value
				j += 1			
			rowCount += 1
			if (rowCount == eigenface_count):
				break

		eigenface_count = int(min(eigenface_count, rowCount))
		eigenfaces = np.zeros((eigenface_count, OUTPUT_SIZE[0] * OUTPUT_SIZE[1]))

		for i in range(0, eigenface_count):
			eigenfaces[i, :] = rows[i, :]

	return mean, eigenfaces
		
def write_facial_image_to_file(personId = -1, image = None):
	directory = (IMAGE_PATH + '/facial_images/person_%s') % personId
	imageId = 0

	if not (os.path.isdir(directory)):
		os.mkdir(directory)
	else:
		imageId = len(list(os.scandir(directory)))

	imwrite(((directory + "/%s.jpg") % imageId), image)

def read_test_image(name, directory = IMAGE_PATH + "/test_images/"):
	return imread(directory + name, IMREAD_GRAYSCALE)

def read_image(file_path):
	image = imread(file_path)
	if (image is None):
		return None, -1, -1, -1, -1
	m, n, p = image.shape

	if (m > 1000 or n > 1000):
		image = resize(image, dsize = None, fx = 0.7, fy = 0.7)
		pass
	else:
		if (m > 2000 or n > 2000):
			image = resize(image, dsize = None, fx = 0.4, fy = 0.4)
	m, n, tempX, tempY = ut.get_size_and_ranges(image)			
	return image, m, n, tempX, tempY

def write_temp_image(image, directory = None):
	if (directory is None):
		directory = IMAGE_PATH + "/temp.jpg"

	imwrite(directory, image)
	return directory

def create_person_directory(personId):
	directory = IMAGE_PATH + "/person_%s" % personId
	if not (os.path.isdir(directory)):
		os.mkdir(directory)

def remove_person_directory(personId, directory = None):
	if (directory is None):
		directory = IMAGE_PATH + "/person_%s" % personId

	if (os.path.isdir(directory)):
		entries = os.scandir(directory)
		for entry in entries:
			os.remove(entry.path)
		os.rmdir(directory)

def remove_image(file_path):
	if (os.path.isfile(file_path)):
		os.remove(file_path)
		return True
	return False