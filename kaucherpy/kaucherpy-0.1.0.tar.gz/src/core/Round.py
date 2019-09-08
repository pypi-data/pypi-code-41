from kaucherpy.core.fenv import *

__all__ = [
    "Round"
]

class Round(object):

	@staticmethod
	def set_down_rounding():
		ROUND.set(ROUND.DOWNWARD)

	@staticmethod
	def set_up_rounding():
		ROUND.set(ROUND.UPWARD)

	@staticmethod
	def set_normal_rounding():
		ROUND.set(ROUND.TONEAREST)

	@staticmethod
	def get_rounding():
		return (ROUND.get())
