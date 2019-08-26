import re
from .matchers import *
from .classification import *

# defines a rule for matching text in the input string
class rule:
	def __init__(self, rule_str):
		
		# store the rule string for debugging
		self.rule_str = rule_str
		
		# regex of allowed matcher formats
		fmts = '(?:' + pattern_matcher.fmt + '|' + type_matcher.fmt + ')'
		
		# split around the 'is' keyword
		m = re.match('(' + fmts + '(?:,' + fmts + ')*)\s+is\s+(.*)', rule_str)
		
		# check rule was valid
		if m is None:
			raise Exception('unknown rule: ' + rule_str)
			
		# extract the list of match expressions
		match_exprs = re.findall(fmts, m.group(1))
		
		# extract the list of type classifications
		is_types = m.group(2).split(',')
		
		# set the rule is-type, if applicable
		self.is_type = is_types[0] if len(is_types) == 1 else None
		
		# check match expressions and types line up
		if len(is_types) > 1 and len(match_exprs) != len(is_types):
			raise Exception('match, type mismatch')
			
		# for each match expression
		self.matchers = []
		for i in range(len(match_exprs)):
			
			# determine matcher is-type
			is_type = self.is_type or is_types[i]
			
			if match_exprs[i].startswith('/'):
				
				# if expression is regex, build pattern matcher
				self.matchers.append(pattern_matcher(match_exprs[i], is_type))
				
			else:
				
				# otherwise, build type matcher
				self.matchers.append(type_matcher(match_exprs[i], is_type))
			
	def match(self, tokens, types):
		
		# for each token
		i = 0
		while i < len(tokens):
			
			new_types = []
			
			# reset number of matched tokens for rule
			n = 0
			
			# reset match count for matcher
			k = 0
			
			# for each matcher
			j = 0
			while j < len(self.matchers):
				matcher = self.matchers[j]
				
				# calculate token index, t
				t = i + n + k
				
				# match token using current matcher
				if matcher.match(tokens[t], t, types):
					
					# if is-type is given
					if len(matcher.is_type) > 0:
						
						# if is-type per matcher
						if self.is_type is None:
							
							# if first match for matcher
							if k == 0:
								
								# create classification
								new_types.append(classification(t, t, matcher.is_type))
								
							else:
								
								# update classification
								new_types[-1].end_token = t
								
						else:
							
							# if first match for rule
							if j == 0 and k == 0:
								
								# create classification
								new_types.append(classification(t, t, self.is_type))
								
							else:
								
								# update classification
								new_types[-1].end_token = t
						
					# if can only match one token
					if matcher.quantifier in ['/', '?']:
						
						# next matcher
						j += 1
						
						# increment match count for rule
						n += 1
						
					else:
						
						# next match with current matcher
						k += 1
						
					# if end then break
					if i + n + k == len(tokens):
						
						# add matcher match count to rule match count
						n += k
						
						break
					
				else:
					
					# if first match attempt and need match
					if k == 0 and matcher.quantifier in ['+', '/']:
						
						# reset matched types and break
						new_types = []
						break
						
					else:
						
						# next matcher
						j += 1
						
						# add matcher match count to rule match count
						n += k
						
						# reset matcher match count
						k = 0
						
			# if rule matched
			if len(new_types) > 0:
				
				# add types from this rule to the type store
				for new_type in new_types:
					types.append(new_type)
					
				# add rule match count to start index
				i += n
			
			else:
				# next start point
				i += 1
