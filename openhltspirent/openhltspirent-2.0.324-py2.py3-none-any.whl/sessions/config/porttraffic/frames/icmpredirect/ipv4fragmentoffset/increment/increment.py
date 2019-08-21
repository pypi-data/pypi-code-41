from openhltspirent.base import Base
class Increment(Base):
	"""The values that make up the increment pattern
	"""
	YANG_NAME = 'increment'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Count": "count", "Start": "start", "Step": "step"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Increment, self).__init__(parent)

	@property
	def Start(self):
		"""The start value of the increment pattern

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('start')

	@property
	def Step(self):
		"""The step value of the increment pattern

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('step')

	@property
	def Count(self):
		"""TBD

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('count')

	def update(self, Start=None, Step=None, Count=None):
		"""Update the current instance of the `increment` resource

		Args:
			Start (string): The start value of the increment pattern
			Step (string): The step value of the increment pattern
			Count (string): TBD
		"""
		return self._update(locals())

