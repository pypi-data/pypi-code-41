from __future__ import absolute_import, division, print_function, unicode_literals

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from typing import MutableSequence

from past.builtins import cmp

def _insertion(seq, cmp_, left, right, gap):
	# type: (MutableSequence, Callable, int, int, int)

	# print("_insertion", left, right, gap)

	loc = left+gap
	while loc <= right:
		i = loc - gap
		value = seq[loc]
		while i >= left and cmp_(seq[i], value) > 0:
			seq[i+gap] = seq[i]
			i -= gap
		seq[i+gap] = value
		loc += gap

GROUP_SIZE = 5

def median_of_medians(seq, cmp_=None, left=None, right=None, gap=1):
	# type: (MutableSequence, Callable, int, int, int)

	""" Approximate median selection algorithm. """

	cmp_ = cmp_ or cmp

	if not left:
		left = 0
	if not right:
		right = len(seq) - 1

	span = GROUP_SIZE*gap
	num = (right - left + 1) // span

	# print("median_of_medians", left, right, gap, span, num)

	if num == 0:
		_insertion(seq, cmp_, left, right, gap)
		num = (right - left + 1) // gap
		return left + gap*(num-1) // 2

	s = left
	while s < right-span:
		_insertion(seq, cmp_, s, s + span - 1, gap)
		s += span

	if num < GROUP_SIZE:
		_insertion(seq, cmp_, left+span // 2, right, span)
		return left + num*span // 2
	else:
		return median_of_medians(seq, cmp_, left + span // 2, s-1, span)

from genutility.test import MyTestCase, parametrize

class AlgorithmsTest(MyTestCase):

	@parametrize(
		([0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 3, 3, 4], 7, 1),
		([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 7, 1),
		([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14], 7, 7),
		([4, 3, 3, 2, 2, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0], 7, 1),
		([1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 2], 7, 3),
		([14, 94, 41, 69, 47, 96, 90, 46, 33, 21, 89, 60, 63, 0, 49], 7, 47),
		([646, 624, 329, 47, 845, 221, 15, 92, 940, 831, 169, 190, 83, 599, 636, 496, 785, 701, 105, 807, 384, 605, 285, 219, 931, 185, 863, 68, 837, 165, 717, 608, 347, 713, 593, 191, 180, 405, 649, 744, 170, 490, 407, 659, 541, 342, 72, 6, 510, 101, 757, 203, 724, 792, 477, 361, 993, 836, 640, 74, 882, 31, 622, 18, 764, 698, 444, 62, 965, 692, 32, 956, 980, 621, 103, 45, 828, 70, 768, 161, 296, 200, 676, 44, 90, 753, 535, 274, 230, 871, 404, 741, 922, 78, 28, 908, 313, 184, 543, 536], 39, 744),
	)
	def test_median_of_medians(self, list, truth_idx, truth_val):
		result = median_of_medians(list)
		self.assertEqual(result, truth_idx)
		self.assertEqual(list[result], truth_val)

if __name__ == "__main__":
	import unittest
	unittest.main()
