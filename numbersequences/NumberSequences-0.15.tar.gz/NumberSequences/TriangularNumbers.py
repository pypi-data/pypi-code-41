class TriangularNumbers:
    """Tools for working with the triangular number sequence A000217"""
    """Ref: https://oeis.org/A000217"""

    def calculate_term(self, argument):
        """Calculate the Nth triangular number"""
        if isinstance(argument, int):
            res = (argument * (argument + 1)) / 2
            return int(res)

    def about(self):
        """Display information about triangular numbers"""
        stub1 = "A triangular number or triangle number counts objects arranged in an equilateral triangle.\r\n"
        stub2 = "The nth triangular number is the number of dots in the triangular arrangement with n dots on a side,\r\n"
        stub3 = "and is equal to the sum of the n natural numbers from 1 to n.\r\n"
        return stub1 + stub2 + stub3


if __name__ == "__main__":
    print("usage:\tcalculate_triangular N")
    print("N\tSpecify the Nth triangular term to calculate")
