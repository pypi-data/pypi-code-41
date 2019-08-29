#cat
def run(args):
	try:
		with open(args, "r") as infile:
			for line in infile:
				print(line, end = "")
	except IOError:
   		print("Error: can\'t find file or read data")
	else:
		print("\n")