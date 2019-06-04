def split_to_get_face(image, pivot, dist, file_output, ratio = (-0.5, 1.5, -0.9, 0.9), output_size = OUTPUT_SIZE):
	if len(image.shape) == 2:
		m, n = image.shape
	else:
		m, n, p = image.shape

	top = int(max(0, (pivot[1] + ratio[0] * dist)))
	bottom = int(min(m - 1, (pivot[1] + ratio[1] * dist)))
	left = int(max(0, (pivot[0] + ratio[2] * dist)))
	right = int(min(n - 1, (pivot[0] + ratio[3] * dist)))
	
	tempImage = image[top:bottom, left:right]
	tempImage = cv2.resize(tempImage, output_size)

	if (file_output):
		cv2.imshow("Facial image", tempImage)
		cv2.waitKey(100)

		check = input("Is it a facial image?(y/n)")
		if (check != 'y'):
			return

		personID = int(input("Person ID:"))
		#return the matched person or the person with largest person id
		person = db.get_people(personID)

		if (person.first() is None or person.first().Id != personID):
			check = input("This person's information doesn't exist. Create new one (y/n):")

			if (check == 'y'):
				name = input("Name:")
				age = int(input("Age:"))
				occupation = input("Occupation:")

				db.create_people([name, age, occupation])
				check = True
				if (person.first() is not None):
					personID = person.first().Id + 1
				else:
					personID = 1
				print("This person id will be:%s" % personID)
			else:
				check = None

		if not (check is None):
			fm.write_facial_image_to_file(personID, tempImage)		
			# return 'hello'
		cv2.destroyWindow("Facial image")
	# return 'hallo'
