
__all__ = ['List', 'JsonSerializable', 'objectToDict','objectToStr',
		'objectFromDict','objectFromStr','objectsFromStr',
		'objectsFromList','objectsToList','objectsToStr']

import json
import six

if six.PY2:
	originType = (str,int,float,long,bool,list,dict,tuple,unicode,set)
elif six.PY3:
	originType = (str,int,float,bool,list,dict,tuple,set)

def objectToDict(self):
	result = dict()
	for (key, value) in self.__dict__.items():
		if isinstance(value, originType) :
			if isinstance(value, list) :
				mapObj = map(lambda item: (item if isinstance(item, originType) else item.objectToDict()), value)
				result[key] = mapObj if six.PY2 else list(mapObj)
			else:
				result[key] = self.__dict__[key]
		else :
			result[key] = value.objectToDict()
	return result

def objectToStr(self):
	return str(self.objectToDict())

def objectsToList(self):
	return map(lambda item: item.objectToDict(), self)

def objectsToStr(self):
	return str(objectsToList(self))

@classmethod
def objectFromDict(cls, pDict):
	instance = cls()
	for (key, value) in pDict.items():
		if type(value).__name__ == 'dict' :
			setattr(instance, key, getattr(instance,key).objectFromDict(value))
		elif type(value).__name__ == 'list' :
			if not isinstance(getattr(instance, key), list):
				clz = list(getattr(instance, key))[0]
				setattr(instance, key, clz.objectsFromList(value))
			else:
				setattr(instance, key, value)
		else:
			setattr(instance, key, value)
	return instance

@classmethod
def objectsFromList(cls, pList):
	lists = List()
	for item in pList:
		instance = cls()
		if type(item).__name__ == 'dict' :
			instance = cls.objectFromDict(item)
		elif type(item).__name__ == 'list' :
			pass
		else:
			pass
		lists.append(instance)
	return lists

@classmethod
def objectFromStr(cls, str):
	result = json.loads(str)
	if type(result).__name__ == 'dict':
		return cls.objectFromDict(result)
	elif type(result).__name__ == 'list':
		return cls.objectsFromList(result)
	return None

@classmethod
def objectsFromStr(cls, str):
	result = json.loads(str)
	if type(result).__name__ == 'list':
		return cls.objectsFromList(result)	
	return None

def JsonSerializable(cls):
	cls.objectToDict 	= objectToDict
	cls.objectToStr 	= objectToStr
	cls.objectFromDict 	= objectFromDict
	cls.objectFromStr 	= objectFromStr
	cls.objectsFromStr 	= objectsFromStr
	cls.objectsFromList = objectsFromList
	cls.objectsToList 	= objectsToList
	cls.objectsToStr 	= objectsToStr
	return cls

@JsonSerializable
class List(list):
	pass
