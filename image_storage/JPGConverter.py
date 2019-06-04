import sys
import cv2
import os

MEAN_PATH = "./eigenface_images/mean"
FACIAL_IMAGES = "./facial_images"

def convert_mean():
	image = cv2.imread(MEAN_PATH + ".jpg")
	cv2.imwrite(MEAN_PATH + ".bmp", image)

def convert_faces():
	entries = os.scandir(FACIAL_IMAGES)

	for entry in entries:
		imageEntries = os.scandir(entry.path)

		for imageEntry in imageEntries:
			image = cv2.imread(imageEntry.path)

			newFile = imageEntry.path[:-3] + "bmp"
			cv2.imwrite(newFile, image)

def remove_jpg():
	# os.remove(MEAN_PATH + ".jpg")

	facial_folders = os.scandir(FACIAL_IMAGES)
	for folder in facial_folders:
		files = os.scandir(folder.path)
		for file in files:
			if (file.path[-3:] == "jpg"):
				os.remove(file.path)

if (__name__ == "__main__"):
	remove_jpg()
	# convert_mean()
	# convert_faces()
