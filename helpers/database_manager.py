from sqlalchemy import create_engine, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker, relationship

import utils as ut

engine = create_engine("mysql+pymysql://root:caothanhhuyen123@localhost:3306/face_recognition")
Session = sessionmaker(bind =  engine)

Base = declarative_base()

class Person(Base):
	__tablename__ = "People"

	Id = Column(Integer, primary_key = True)
	Name = Column(String(250))
	Age = Column(Integer)
	Occupation = Column(String(250))

	SubspaceImages = relationship("SubspaceImage",
		cascade = "all, delete, delete-orphan")

class SubspaceImage(Base):
	__tablename__ = "SubspaceImages"

	Id = Column(Integer, primary_key = True)
	Path = Column(String(250))
	Weights = Column(String(5000))

	OwnerId = Column(Integer, ForeignKey("People.Id",
		ondelete='CASCADE'))
	Owner = relationship("Person")

	def get_weights_as_array(self):
		values = self.Weights.split(',')
		result = []

		for value in values:
			# print(values[i])
			result.append(float(value))

		return result

def create_tables():
	Base.metadata.bind = engine	
	Base.metadata.create_all()

def renew_tables():
	SubspaceImage.__table__.drop(engine)
	Person.__table__.drop(engine)
	#SubspaceImages.__table__.drop(engine)

	create_tables()

def renew_subspaceimages_table():
	SubspaceImage.__table__.drop(engine)
	SubspaceImage.__table__.create(engine)

def get_people(allFlag = False, *ids):
	session = Session()
	people = None
	
	if (len(ids) > 0):
		people = session.query(Person).filter(Person.Id.in_(ids))
	if (people is None):
		if not (allFlag):
			maxid = session.query(func.max(Person.Id))[0][0]		
			people = session.query(Person).filter(Person.Id == maxid)
		else:
			people = session.query(Person).all()

	session.close()
	return people

def get_people_count():
	session = Session()
	result = session.query(func.count(Person.Id))
	session.close()
	return result[0][0]

def get_max_personid():
	session = Session()
	result = session.query(func.max(Person.Id))[0][0]
	session.close()
	return result

def get_subspace_images(ids = None):
	session = Session()
	if (ids is None):
		result = session.query(SubspaceImage).all()
	else:
		result = session.query(SubspaceImage).filter(SubspaceImage.Id.in_(ids))
	session.close()
	return result

def create_people(*people_data):
	'''each person data will be saved in the form of name, age, occupation'''	
	session = Session()

	people = []
	for personData in people_data:
		if (len(personData) >= 3):
			person = Person(Name = personData[0], Age = int(personData[1]), Occupation = personData[2])
			people.append(person)

	if (len(people) > 0):
		session.add_all(people)
		session.commit()
	session.close()

def update_people(*people_data):
	session = Session()
	for personData in people_data:
		session.query(Person).filter(Person.Id == int(personData[0]))\
			.update({Person.Name: personData[1], Person.Age: int(personData[2]), Person.Occupation: personData[3]}, 
				synchronize_session = False)
	session.commit()

def delete_people(*people_data):
	session = Session()
	peopleIds = []

	for personData in people_data:
		peopleIds.append(int(personData[0]))
	statement = Person.__table__.delete().where(Person.Id.in_(peopleIds))

	session.execute(statement)
	session.commit()
	session.close()	

def create_subspace_images(file_info, weights, remove = False):
	if (remove):
		delete_subspace_images(None)

	Images = []
	temp = range(0, len(file_info))

	for i in temp:
		Images.append(SubspaceImage(Path = file_info[i][1], 
			OwnerId = file_info[i][0], Weights = ut.concatenate_into_string(weights[i])))

	session = Session()
	session.add_all(Images)
	session.commit()
	session.close()

def delete_subspace_images(file_paths = None):
	if (file_paths is None):
		session = Session()
		session.execute('''TRUNCATE TABLE SubspaceImages''')
		session.commit()
		session.close()
		return

	session = Session()
	statement = SubspaceImage.__table__.delete().where(SubspaceImage.Path.in_(file_paths))
	session.execute(statement)
	session.commit()
	session.close()

def clean_up():
	engine.dispose()

if (__name__ == "__main__"):
	# renew_tables()
	# clean_up()
	pass
