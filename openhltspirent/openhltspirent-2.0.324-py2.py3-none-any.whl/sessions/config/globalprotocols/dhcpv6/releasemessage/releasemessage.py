from openhltspirent.base import Base
class ReleaseMessage(Base):
	"""Release message options
	"""
	YANG_NAME = 'release-message'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(ReleaseMessage, self).__init__(parent)

	@property
	def InitialTimeout(self):
		"""Specifiy the time (in seconds) that the host waits to receive
		a REPLY message from the delegating router after sending an initial
		RELEASE message.If the host does not receive a valid REPLY message
		within this time,it sends another RELEASE message and the timeout
		length is doubled fromthe previous attempt.

		Get an instance of the InitialTimeout class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.releasemessage.initialtimeout.initialtimeout.InitialTimeout)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.releasemessage.initialtimeout.initialtimeout import InitialTimeout
		return InitialTimeout(self)._read()

	@property
	def RetryCount(self):
		"""Number of release retries.

		Get an instance of the RetryCount class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.releasemessage.retrycount.retrycount.RetryCount)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.releasemessage.retrycount.retrycount import RetryCount
		return RetryCount(self)._read()

	@property
	def IndefiniteRetry(self):
		"""Flag indicating releases will retried indefinitely.
		TRUE  : Enable indefinite retry of releases.
		FALSE : Disable indefinite retry of releases.

		Get an instance of the IndefiniteRetry class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.releasemessage.indefiniteretry.indefiniteretry.IndefiniteRetry)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.releasemessage.indefiniteretry.indefiniteretry import IndefiniteRetry
		return IndefiniteRetry(self)._read()

	@property
	def DisableRetries(self):
		"""Flag indicating releases will be not be retried.
		TRUE  : Disable retry of releases.
		FALSE : Enable retry of releases.

		Get an instance of the DisableRetries class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.releasemessage.disableretries.disableretries.DisableRetries)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.releasemessage.disableretries.disableretries import DisableRetries
		return DisableRetries(self)._read()

	def create(self):
		"""Create an instance of the `release-message` resource

		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `release-message` resource

		"""
		return self._delete()

