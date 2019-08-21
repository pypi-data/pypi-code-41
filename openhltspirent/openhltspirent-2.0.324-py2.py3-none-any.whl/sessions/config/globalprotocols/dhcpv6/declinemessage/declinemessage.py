from openhltspirent.base import Base
class DeclineMessage(Base):
	"""Decline message options
	"""
	YANG_NAME = 'decline-message'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(DeclineMessage, self).__init__(parent)

	@property
	def InitialTimeout(self):
		"""Specifiy the time (in seconds) that the host waits to receive a REPLY message
		after sending a DECLINE message.If the host does not receive a valid REPLY
		message within this time,it sends another DECLINE message and the timeout
		length is doubled from the previous attempt.

		Get an instance of the InitialTimeout class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.declinemessage.initialtimeout.initialtimeout.InitialTimeout)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.declinemessage.initialtimeout.initialtimeout import InitialTimeout
		return InitialTimeout(self)._read()

	@property
	def RetryCount(self):
		"""Number of decline retries.

		Get an instance of the RetryCount class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.declinemessage.retrycount.retrycount.RetryCount)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.declinemessage.retrycount.retrycount import RetryCount
		return RetryCount(self)._read()

	@property
	def IndefiniteRetry(self):
		"""Flag indicating declines will retried indefinitely.
		TRUE  : Enable indefinite retry of declines.
		FALSE : Disable indefinite retry of declines.

		Get an instance of the IndefiniteRetry class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.declinemessage.indefiniteretry.indefiniteretry.IndefiniteRetry)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.declinemessage.indefiniteretry.indefiniteretry import IndefiniteRetry
		return IndefiniteRetry(self)._read()

	@property
	def DisableRetries(self):
		"""Flag indicating declines will be not be retried.
		TRUE  : Disable retry of declines.
		FALSE : Enable retry of declines.

		Get an instance of the DisableRetries class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.declinemessage.disableretries.disableretries.DisableRetries)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.declinemessage.disableretries.disableretries import DisableRetries
		return DisableRetries(self)._read()

	def create(self):
		"""Create an instance of the `decline-message` resource

		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `decline-message` resource

		"""
		return self._delete()

