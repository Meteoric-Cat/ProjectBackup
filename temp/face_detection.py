from sys import setrecursionlimit, path 

import cv2
import find_face_candidate as ffc 
import numpy as np
import gc
import os

import utils as ut
import database_manager as db 

if (__name__ == "__main__"):
	setrecursionlimit(100000)

	temp = input("Input name of the image:")
	imagePath = '../input/lfw/AGOODIMAGES/Angelina_Jolie/Angelina_Jolie_001%s.jpg' % temp
	image = cv2.imread(imagePath)

	m, n, tempX, tempY = ut.get_size_and_ranges(image)
	if (m > 1000 or n > 1000):
		image = cv2.resize(image, dsize = None, fx = 0.7, fy = 0.7)
		pass
	else:
		if (m > 2000 or n > 2000):
			image = cv2.resize(image, dsize = None, fx = 0.4, fy = 0.4)
	m, n, tempX, tempY = ut.get_size_and_ranges(image)

	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.float)

	ffc.get_possible_face_regions(image, m, n, tempX, tempY)

	db.clean_up()
	gc.collect()

