from .matchers import *
from .classification import *

class classifications:
	def __init__(self, token_list, classification_list):
		self.token_list = token_list
		self.classification_list = classification_list
	
	def extract_typed(self, type):
		def get_token_str(c):
			tstr = ''
			for i in range(c.start_token, c.end_token + 1):
				if len(tstr) > 0:
					tstr += ' '
				tstr += self.token_list[i]
			return tstr
			
		return [get_token_str(c) for c in self.classification_list if c.type == type]
		
	def __str__(self):
		str = ''
		types = []
		before_close_len = 0
		for i in range(len(self.token_list)):
			before_open_len = len(types)
			
			# write opening tag for each classification starting on this token index
			def by_end(c):
				return c.end_token
			sorted_cls = self.classification_list.copy()
			sorted_cls.sort(key=by_end, reverse=True)
			for classification in sorted_cls:
				if classification.start_token == i:
					str += '<' + classification.type + '>'
					types.append(classification.type)
					
			# if no new opening tags, separate with space
			if len(types) == before_close_len and len(types) == before_open_len:
				str += ' '
			
			# write the token content
			str += self.token_list[i]
			
			# try to close each open tag (most recent first), stopping at the first one that isn't ended at this token
			before_close_len = len(types)
			while len(types) > 0:
				found = False
				for classification in self.classification_list:
					if classification.end_token == i and classification.type == types[-1]:
						str += '</' + types.pop() + '>'
						found = True
						if len(types) == 0:
							break
				if found == False:
					break
					
		return str
		
