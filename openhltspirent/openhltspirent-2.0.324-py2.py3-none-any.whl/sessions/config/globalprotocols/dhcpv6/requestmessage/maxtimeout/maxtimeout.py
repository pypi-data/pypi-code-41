from openhltspirent.base import Base
class MaxTimeout(Base):
	"""Specify the maximum timeout value (in seconds) that the host waits
	for an REPLY message.
	If an initial REQUEST message is unsuccessful and times out, the
	timeoutvalue for subsequent attempts is either double the previous
	timeout value or the value specified for this field, whichever is
	lower. Thisfield limits the retry timeout time, which can become
	long if it continuesto double with each retry. If the REQUEST
	timeout value is set to the MaximumRequest Retry Timeout value,
	the client tries to resend the REQUESTmessage for the number of
	times specified in the Request Retry Count field.
	"""
	YANG_NAME = 'max-timeout'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Single": "single", "PatternType": "pattern-type", "PatternFormat": "pattern-format", "ValueList": "value-list"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(MaxTimeout, self).__init__(parent)

	@property
	def Increment(self):
		"""The values that make up the increment pattern

		Get an instance of the Increment class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.requestmessage.maxtimeout.increment.increment.Increment)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.requestmessage.maxtimeout.increment.increment import Increment
		return Increment(self)._read()

	@property
	def Decrement(self):
		"""TBD

		Get an instance of the Decrement class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.requestmessage.maxtimeout.decrement.decrement.Decrement)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.requestmessage.maxtimeout.decrement.decrement import Decrement
		return Decrement(self)._read()

	@property
	def Random(self):
		"""The repeatable random pattern.

		Get an instance of the Random class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.requestmessage.maxtimeout.random.random.Random)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.requestmessage.maxtimeout.random.random import Random
		return Random(self)._read()

	@property
	def PatternType(self):
		"""The selected pattern from the possible pattern types.

		Getter Returns:
			SINGLE | INCREMENT | DECREMENT | RANDOM | VALUE_LIST

		Setter Allows:
			SINGLE | INCREMENT | DECREMENT | RANDOM | VALUE_LIST

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('pattern-type')

	@property
	def PatternFormat(self):
		"""The format of the pattern.
		This will almost always be a regular expression.
		It is used to determine the validity of the values being set in the child leaf nodes of the pattern.

		Getter Returns:
			string
		"""
		return self._get_value('pattern-format')

	@property
	def Single(self):
		"""The value of the single pattern

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
		"""The value list pattern takes a list of values that will be repeated if they do not meet or exceed the count

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('value-list')

	def update(self, PatternType=None, PatternFormat=None, Single=None, ValueList=None):
		"""Update the current instance of the `max-timeout` resource

		Args:
			PatternType (enumeration): The selected pattern from the possible pattern types.
			PatternFormat (string): The format of the pattern.This will almost always be a regular expression.It is used to determine the validity of the values being set in the child leaf nodes of the pattern.
			Single (string): The value of the single pattern
			ValueList (string): The value list pattern takes a list of values that will be repeated if they do not meet or exceed the count
		"""
		return self._update(locals())

