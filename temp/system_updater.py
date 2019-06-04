import eigenface_implementer as pca 
from constants import MAX_EIGENFACE_COUNT 

def update(system_data):
	mean, eigenfaces = pca.find_meanface_and_eigenfaces(MAX_EIGENFACE_COUNT)
	system_data.update(mean, eigenfaces)


