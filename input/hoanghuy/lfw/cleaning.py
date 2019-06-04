import sys
import os

if (__name__=="__main__"):
	entries = os.scandir(".")
	STORAGE = "./A"

	for entry in entries:
		temp = os.scandir(entry.path)

		count = 0
		for value in temp:
			count += 1

		if (count <= 1):
			
