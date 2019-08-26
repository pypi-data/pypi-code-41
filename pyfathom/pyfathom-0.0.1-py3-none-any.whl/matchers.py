import re

# matches parts of the input string
class matcher:
	def __init__(self, is_type):
		self.is_type = is_type

# matches single token with a regex pattern
class pattern_matcher(matcher):
	
	fmt = '\\/(?:\\\\\\\\|\\\\\\/|[^\\/])+\\/[\+\*\?]?'
	
	def __init__(self, pattern, is_type):
		super(pattern_matcher, self).__init__(is_type)
		self.pattern = '^(?:' + (pattern[1:-1] if pattern[-1] == '/' else pattern[1:-2]) + ')$'
		self.quantifier = pattern[-1]
	
	def match(self, token, idx, types):
		return re.match(self.pattern, token) is not None
		
	def __repr__(self):
		return '/' + self.pattern + '/'
	
# matches a single token with a type
class type_matcher(matcher):
	
	fmt = '[\w\|-]+\??'
	
	def __init__(self, types, is_type):
		super(type_matcher, self).__init__(is_type)
		self.types = types.rstrip('?').split('|')
		self.quantifier = '*' if types[-1] == '?' else '+'
	
	def match(self, token, idx, types):
		for t in types:
			if t.start_token <= idx and t.end_token >= idx and t.type in self.types:
				return True
		return False
		
	def __repr__(self):
		return '|'.join(self.types)

