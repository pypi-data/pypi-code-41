from openhltspirent.base import Base
class IncrementRate(Base):
	"""TBD
	"""
	YANG_NAME = 'increment-rate'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Count": "count", "PercentValue": "percent-value", "Mbps": "mbps", "Step": "step", "RateType": "rate-type", "Bps": "bps", "Fps": "fps", "Kbps": "kbps"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(IncrementRate, self).__init__(parent)

	@property
	def RateType(self):
		"""Load unit applied to the stream block.

		Getter Returns:
			BPS | KBPS | MPBS | FRAMES_PER_SECOND | PERCENT_LINE_RATE

		Setter Allows:
			BPS | KBPS | MPBS | FRAMES_PER_SECOND | PERCENT_LINE_RATE

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('rate-type')

	@property
	def Bps(self):
		"""Load value set on the streamblock/traffic-item in bits per second.

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('bps')

	@property
	def Kbps(self):
		"""Load value set on the streamblock/traffic-item in kilo bits per second.

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('kbps')

	@property
	def Mbps(self):
		"""Load value set on the streamblock/traffic-item in mega bits per second.

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('mbps')

	@property
	def Fps(self):
		"""Load value set on the streamblock/traffic-item in frames per second.

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('fps')

	@property
	def PercentValue(self):
		"""Load value set on the streamblock/traffic-item in percent.

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('percent-value')

	@property
	def Count(self):
		"""Maximum increment value for frame length

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('count')

	@property
	def Step(self):
		"""Step increment value for frame length

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('step')

	def update(self, RateType=None, Bps=None, Kbps=None, Mbps=None, Fps=None, PercentValue=None, Count=None, Step=None):
		"""Update the current instance of the `increment-rate` resource

		Args:
			RateType (enumeration): Load unit applied to the stream block.
			Bps (int32): Load value set on the streamblock/traffic-item in bits per second.
			Kbps (int32): Load value set on the streamblock/traffic-item in kilo bits per second.
			Mbps (int32): Load value set on the streamblock/traffic-item in mega bits per second.
			Fps (int32): Load value set on the streamblock/traffic-item in frames per second.
			PercentValue (int32): Load value set on the streamblock/traffic-item in percent.
			Count (int32): Maximum increment value for frame length
			Step (int32): Step increment value for frame length
		"""
		return self._update(locals())

