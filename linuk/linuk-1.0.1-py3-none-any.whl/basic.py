
def listmaker(object,include_space=False,data_type=str):
	'''Makes List from space separated strings 
	Example: listmaker('object1 object2 object3')

PARAMETERS:
	include_space : bool, default=False
		listmaker('object_1 object_2 object_3')
		'_' is interpreted as space

	data_type : Datatype, default=str
		change Datatype of Objects
		available datatypes{int,str,float}

	

	'''
	madelist = object.split(' ')
	if include_space==True:
		for i in range(len(madelist)):
			madelist[i]  =  madelist[i].replace('_',' ')

	for i in range(len(madelist)):
			madelist[i]  =  data_type(madelist[i])

	return madelist
