import re

def is_number(n):
    try:
        float(n)   # Type-casting the string to `float`.
                   # If string is not a valid `float`, 
                   # it'll raise `ValueError` exception
    except ValueError:
        return False
    return True

def compiler():
	global write_filename
	import os
	import sys
	current_location = os.path.dirname(sys.executable)
	os.system(f"pyinstaller {write_filename} --onefile --distpath {current_location} --noconfirm")
	
	return None

def write_python(code):
	global write_filename
	with open(write_filename, 'w') as f:
		f.write(code)

def make_code(code_list):
	outlst = [''.join([str(c) for c in lst]) for lst in code_list]
	print(outlst)
	code = ''.join(c for c in outlst)
	code += '\nif __name__ == "__main__":\n    main()\n'
	print("\n\nTranslated code:")
	print(code)
	print("\nEnd translated code.")
	return code

def tokenizer(lines, the_tabs):
	global parsed_code_list, string_pattern

	# Add non-Python builtins.

	current_switch_value = None
	skipping_line = False 
	for hello in range(len(lines)):
		line = lines[hello]
		if skipping_line == False:
			x = 0
			while x < the_tabs:
					to_append.append('    ')
					x += 1

			if True:
				to_append = []
				line_ended = False
				asdf = 0
				x=0

				
				while asdf < len(line) and line_ended == False:
					i = line[asdf]
					if string_pattern.match(i):
						to_append.append(i)

					elif i == "analog":
						expression_string = 'analog('
						x = line.index('analog')
						while x <= len(line) - 1:
							if line[x] != '}':
								expression_string += (line[x])
								x += 1
							else:
								the_tabs -= 1
								break

					elif i == "//":
						to_append.append('#')
					elif i == 'using':
						to_append.append('import')
					elif i == 'end':
						to_append.append('quit()')
					elif i == 'function':
						the_string = ' '.join(line)
						to_append.append('def')
					elif i == '{':
						to_append.append(':')
						the_tabs += 1
					elif i == '}':
						the_tabs -= 1
					elif is_number(i) == True:
						to_append.append(i)

					# 'default' keyword.
					elif i == 'default':
						to_append.append('else')
					# 'case' keyword.
					elif i == 'case':
						to_append.append(f'elif {current_switch_value} == {line[asdf + 1]}:')
						the_tabs += 1
						line_ended = True

					elif i == 'cout':
						x = 1
						line.remove('cout')
						expression_string = 'print('
						if len(line) >= 2:
							while x <= len(line)-1:
								if line[x] != '}':
									expression_string += (line[x])
									x += 1
								else:
									the_tabs -= 1
									break
							expression_string += ", end='', flush=True)"
						else:
							expression_string += (line[1] + ", end='')")
						
						to_append.append(expression_string)
						line_ended = True
					elif i == 'cin':
						line.remove('cin')
						x = 3
						expression_string = 'input('
						if len(line) >= 2:
							while x <= len(line)-1:
								if line[x] != '}':
									expression_string += (line[x])
									x += 1
								else:
									the_tabs -= 1
									break
						expression_string += ")"
						to_append.append(expression_string)
						line_ended = True
					# MAKE SURE THE FOLLOWING IS LAST, IS CATCH-ALL FOR NAMES.
					else:
						to_append.append(i)
					asdf += 1
				
			to_append.append('\n')
			parsed_code_list.append(to_append)

def parser(lines):
	global parsed_code_list
	the_tabs = 0
	tokenizer(lines, the_tabs)
	print(parsed_code_list)
	code = make_code(parsed_code_list)
	write_python(code)
	compiler()

def main():
	import argparse
	global string_pattern, plus_pattern, tokenize, the_tabs, parsed_code_list, write_filename
	filename = input("Path to the *.bc file you want compiled, replacing <<\\>> characters with <</>>: ")
	write_filename = filename[:-3]
	write_filename += 'py'
	import re
	string_pattern = re.compile(r'".*?"')
	plus_pattern = re.compile(r'[+]')
	tokenize = re.compile(r'''
	\d* \.? \d+ (?: E -? \d+)?                     | # number
	|[(]|[)]|[{]|[}]|end|[ ]|analog|
	sin|cos|tan|atn|abs|function|cout|cin|[/][/]|[+]|[-]|[/]|[*]|[!@#$%^&*.?\-,;:<>`~]|[\n]|[\b]|[\r]|[\\]| # functions
	\bFalse\b|\bclass\b|\bfinally\b|\bis\b|\breturn\b|\bNone\b|\bcontinue\b|\bfor\b|\blambda\b|\btry\b|\bTrue\b|\bdef\b|\bfrom\b|\bwhile\b|\band\b|\bdel\b|\bglobal\b|\bnot\b|\bwith\b|\bas\b|elif|if|or|yield|assert|else|import|pass|break|except|in|raise| # keywords
	[1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz]*\d? | # variable names (letter + optional digit)
	".*?"|\w|[,]| # labels (strings in double quotes)
	==|
	!=|>=|<=|[=] # multi-character relational operators
	         # any non-space single character ''', 
	re.VERBOSE).findall
	the_tabs = 0
	parsed_code_list = []
	
	with open(filename, 'r') as f:
		text = f.read()
	the_list = [line for line in text.splitlines() if line]
	for x in range(len(the_list)):
		the_list[x] = tokenize(the_list[x])
	
	code_list = []
	for i in range(len(the_list)):
		line_list = []
		for j in range(len(the_list[i])):
			if the_list[i][j] != '':
				line_list.append(the_list[i][j])
		code_list.append(line_list)

	parser(code_list)

if __name__ == "__main__":
	main()