# records a type classification
class classification:
	def __init__(self, start_token, end_token, type):
		self.start_token = start_token
		self.end_token = end_token
		self.type = type
		
	def __repr__(self):
		return '{' + 's:' + str(self.start_token) + ', e:' + str(self.end_token) + ', t:' + self.type + '}'

