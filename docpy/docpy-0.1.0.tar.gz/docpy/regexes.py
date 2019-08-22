import re

def_regex = r"(\t| +)*def \w*\(.*\):"
class_regex = r"(\t| +)*class \w*(\(.*\))?:"

class Object:
	def __init__(self, signature, docstring, is_fn, is_method, is_class, parent=None):
		self.signature = signature
		self.docstring = docstring
		self.is_fn = is_fn
		self.is_method = is_method
		self.is_class = is_class
		self.parent = parent

def parse_file(file):
	"""
	Parses a file object for class, method, and function docstrings.

	Args:
	* `file` (file object): The document to parse

	Returns:
	* `tuple`. Functions, methods, and classes with docstrings
	"""

	lines = file.readlines()
	objects = []
	prev_func, prev_method, prev_class = False, False, False
	in_docstring = False
	signature, docstring, parent_class = "", "", ""

	for line in lines:
		if re.match(def_regex, line):
			signature, docstring = line, ""

			if re.match(r"(\t| )+", line):
				prev_method = True
				prev_func, prev_class = False, False

			else:
				prev_func = True
				prev_method, prev_class = False, False

		elif re.match(class_regex, line):
			signature, docstring, parent_class = line, "", line
			prev_class = True
			prev_func, prev_method = False, False

		elif in_docstring:
			docstring += line

			if "\"\"\"" in line:
				in_docstring = False

				if prev_func:
					objects += [Object(signature, docstring, True, False, False)]
					prev_func = False

				elif prev_method:
					objects += [Object(signature, docstring, False, True, False, parent_class)]
					prev_method = False

				elif prev_class:
					objects += [Object(signature, docstring, False, False, True)]
					prev_class = False


		elif "\"\"\"" in line:
			in_docstring = True
			docstring += line
			line = re.sub("\"\"\"", "", line, count=1)

			if "\"\"\"" in line:
				in_docstring = False

				if prev_func:
					objects += [Object(signature, docstring, True, False, False)]
					prev_func = False

				elif prev_method:
					objects += [Object(signature, docstring, False, True, False, parent_class)]
					prev_method = False

				elif prev_class:
					objects += [Object(signature, docstring, False, False, True)]
					prev_class = False

	return objects