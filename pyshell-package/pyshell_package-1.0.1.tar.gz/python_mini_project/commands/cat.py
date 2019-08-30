# cat command concatenate the entered file

"""This function is called when cat command is entered along with
the required arguments"""


def run(args):
	try:
		with open(args, "r") as infile:
			for line in infile:
				print(line, end="")
			print("\n")
	except IOError:
		from extern import extern_var
		print(extern_var.get('cant_find'))
