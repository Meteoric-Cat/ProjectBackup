import sys
import os
import shutil

if (__name__=="__main__"):
	entries = os.scandir(".")
	STORAGE = "./A"

	for entry in entries:
		if (entry.path == "./cleaning.py"):
			continue
		temp = os.scandir(entry.path)

		count = 0
		for value in temp:
			count += 1

		if (count <= 5):
			shutil.move(entry.path, STORAGE)
