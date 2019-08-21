from openhltspirent.base import Base
class RapidCommitMode(Base):
	"""Rapid commit operation mode.
	DISABLE : Disable rapid commit mode.
	ENABLE  : Enable rapid commit mode and only honor replies with the Rapid Commit option.
	SERVER  : Enable rapid commit mode and continue binding process whether or not the server
	       responds with a Rapid Commit option. The Rapid Commit option isincluded in the
	       ADVERTISE message. If the Rapid Commit option isenabled on the DUT, the two-message
	       exchanged is used. If the RapidCommit option is disabled on the DUT, the four-message
	       exchange is used
	"""
	YANG_NAME = 'rapid-commit-mode'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Single": "single", "PatternType": "pattern-type", "PatternFormat": "pattern-format", "ValueList": "value-list"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(RapidCommitMode, self).__init__(parent)

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
		"""Update the current instance of the `rapid-commit-mode` resource

		Args:
			PatternFormat (string): Refine this leaf value with a regex of valid enum choices
			PatternType (enumeration): TBD
			Single (string): TBD
			ValueList (string): TBD
		"""
		return self._update(locals())

