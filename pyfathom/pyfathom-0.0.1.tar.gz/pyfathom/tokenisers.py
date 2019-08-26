import re

class default_tokeniser:
	def tokenise(self, in_str):
		return [t for t in re.split('([a-zA-Z][a-zA-Z\\-]*|[½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞\\d]+|[^\\w ])', in_str) if t.strip() != '']
