import numpy as np 

def aggregate_subspaceimage_weights(subspace_images):
	result = []
	weight_count = len(subspace_images[0].get_weights_as_array())

	for image in subspace_images:
		temp = image.get_weights_as_array()
		value = np.zeros((1, weight_count))

		value[0, :] = temp[:]
		result.append(value)

	return result



