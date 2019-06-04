import os

if (__name__ == "__main__"):
	limit = int(input("input the maximum id:"))
	# for i in range(1, limit + 1):
		#os.remove("face_database/person%s/*" % i)
	entryList = os.scandir("face_database/")
	for entry in entryList:
		os.remove(entry.path)
