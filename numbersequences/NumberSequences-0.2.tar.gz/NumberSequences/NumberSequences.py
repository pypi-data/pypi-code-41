class TriangularNumbers:
	def calculate_triangular(argument):
		if isinstance(argument, int):
			res = (argument * (argument + 1))/2
			return int(res)
		
if __name__ == "__main__":
	print("usage:\tcalculate_triangular N")
	print("N\tSpecify the Nth triangular term to calculate")