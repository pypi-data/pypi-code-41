from openhltspirent.base import Base
class FrameLength(Base):
	"""TBD
	"""
	YANG_NAME = 'frame-length'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Fixed": "fixed", "LengthType": "length-type"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(FrameLength, self).__init__(parent)

	@property
	def Random(self):
		"""Random frame size options

		Get an instance of the Random class.

		Returns:
			obj(openhltspirent.sessions.config.devicetraffic.framelength.random.random.Random)
		"""
		from openhltspirent.sessions.config.devicetraffic.framelength.random.random import Random
		return Random(self)._read()

	@property
	def Increment(self):
		"""TBD

		Get an instance of the Increment class.

		Returns:
			obj(openhltspirent.sessions.config.devicetraffic.framelength.increment.increment.Increment)
		"""
		from openhltspirent.sessions.config.devicetraffic.framelength.increment.increment import Increment
		return Increment(self)._read()

	@property
	def Decrement(self):
		"""TBD

		Get an instance of the Decrement class.

		Returns:
			obj(openhltspirent.sessions.config.devicetraffic.framelength.decrement.decrement.Decrement)
		"""
		from openhltspirent.sessions.config.devicetraffic.framelength.decrement.decrement import Decrement
		return Decrement(self)._read()

	@property
	def Imix(self):
		"""TBD

		Get an instance of the Imix class.

		Returns:
			obj(openhltspirent.sessions.config.devicetraffic.framelength.imix.imix.Imix)
		"""
		from openhltspirent.sessions.config.devicetraffic.framelength.imix.imix import Imix
		return Imix(self)._read()

	@property
	def LengthType(self):
		"""TBD

		Getter Returns:
			FIXED | INCREMENT | DECREMENT | RANDOM | AUTO | IMIX

		Setter Allows:
			FIXED | INCREMENT | DECREMENT | RANDOM | AUTO | IMIX

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('length-type')

	@property
	def Fixed(self):
		"""Fixed value for frame length

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('fixed')

	def update(self, LengthType=None, Fixed=None):
		"""Update the current instance of the `frame-length` resource

		Args:
			LengthType (enumeration): TBD
			Fixed (int32): Fixed value for frame length
		"""
		return self._update(locals())

