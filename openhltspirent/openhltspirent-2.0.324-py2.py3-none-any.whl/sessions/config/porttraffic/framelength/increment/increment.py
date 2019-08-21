from openhltspirent.base import Base
class Increment(Base):
	"""TBD
	"""
	YANG_NAME = 'increment'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Start": "start", "Step": "step", "End": "end"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Increment, self).__init__(parent)

	@property
	def Start(self):
		"""Starting increment value for frame length

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('start')

	@property
	def End(self):
		"""Maximum increment value for frame length

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('end')

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

	def update(self, Start=None, End=None, Step=None):
		"""Update the current instance of the `increment` resource

		Args:
			Start (int32): Starting increment value for frame length
			End (int32): Maximum increment value for frame length
			Step (int32): Step increment value for frame length
		"""
		return self._update(locals())

