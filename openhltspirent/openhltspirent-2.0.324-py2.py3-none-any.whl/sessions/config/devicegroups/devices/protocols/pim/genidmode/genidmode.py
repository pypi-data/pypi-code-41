from openhltspirent.base import Base
class GenIdMode(Base):
	"""In PIM, routers send the Generation ID as an option in the Hello messages.
	            Every time a router starts up, it selects a random number. The router uses
	            that number as long as it remains operational. If the Generation ID changes,
	            it is an indication to the neighboring routers that this router has gone through
	            a shutdown-restart cycle. This causes the neighboring routers to reset their
	            databases and start fresh. If the generation ID mode is Fixed, it emulates normal
	            PIM router behavior. Incremental or Random means Spirent TestCenter will send
	            different generation IDs in successive Hello messages, causing the DUTs to reset
	            and rebuild their databases often.
	            The interactive menu option, Increment Generation ID, sends one Hello message with
	            incremented Generation ID
	               FIXED	    : Emulates normal PIM router behavior.
	               INCREMENT   : Spirent TestCenter sends different Generation IDs in successive Hello messages,
	                           incrementing by one each time.
	               RANDOM	    : Spirent TestCenter sends different Generation IDs in successive Hello messages,
	                           selecting a random number each time.
	"""
	YANG_NAME = 'gen-id-mode'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Single": "single", "PatternType": "pattern-type", "PatternFormat": "pattern-format", "ValueList": "value-list"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(GenIdMode, self).__init__(parent)

	@property
	def PatternFormat(self):
		"""Refine this leaf value with a regex of valid enum choices

		Getter Returns:
			string
		"""
		return self._get_value('pattern-format')

	@property
	def PatternType(self):
		"""TBD

		Getter Returns:
			SINGLE | VALUE_LIST

		Setter Allows:
			SINGLE | VALUE_LIST

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('pattern-type')

	@property
	def Single(self):
		"""TBD

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('single')

	@property
	def ValueList(self):
		"""TBD

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('value-list')

	def update(self, PatternFormat=None, PatternType=None, Single=None, ValueList=None):
		"""Update the current instance of the `gen-id-mode` resource

		Args:
			PatternFormat (string): Refine this leaf value with a regex of valid enum choices
			PatternType (enumeration): TBD
			Single (string): TBD
			ValueList (string): TBD
		"""
		return self._update(locals())

